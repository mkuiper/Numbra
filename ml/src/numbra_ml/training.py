"""CPU frozen ImageNet features + train-only head, always PLACEHOLDER."""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
from safetensors.torch import load_file
import timm
import torch
from torch import nn

from . import PLACEHOLDER_NOTICE
from .dataset import load_rgb
from .evaluation import ComponentIndex, component_predictions
from .preprocessing import preprocess
from .pretrained import MODEL_NAME, verify_checkpoint


@dataclass(frozen=True)
class TrainingConfig:
    seed: int = 20261009
    epochs: int = 300
    learning_rate: float = 0.03
    weight_decay: float = 0.01
    batch_size: int = 16
    threads: int = 2

    def __post_init__(self):
        if (type(self.seed) is not int or not 0 <= self.seed < 2**32
                or type(self.epochs) is not int or not 1 <= self.epochs <= 10000
                or type(self.batch_size) is not int or not 1 <= self.batch_size <= 128
                or type(self.threads) is not int or not 1 <= self.threads <= 16
                or not np.isfinite(self.learning_rate) or not 0 < self.learning_rate <= 1
                or not np.isfinite(self.weight_decay) or not 0 <= self.weight_decay <= 1):
            raise ValueError("invalid CPU training configuration")


def initialise(config: TrainingConfig) -> None:
    torch.set_num_threads(config.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(config.seed)


def tensor_hash(state: dict[str, torch.Tensor]) -> str:
    digest = hashlib.sha256()
    for key, value in sorted(state.items()):
        array = value.detach().cpu().contiguous().numpy()
        digest.update(json.dumps([key, str(array.dtype), list(array.shape)]).encode())
        digest.update(array.tobytes())
    return digest.hexdigest()


def load_backbone(checkpoint: Path) -> nn.Module:
    verify_checkpoint(checkpoint)
    # pretrained=False prevents timm/hub implicit network or credential access.
    backbone = timm.create_model(MODEL_NAME, pretrained=False)
    backbone.load_state_dict(load_file(str(checkpoint / "model.safetensors"), device="cpu"), strict=True)
    backbone.reset_classifier(0)
    backbone.requires_grad_(False)
    return backbone.cpu().eval()


def extract_features(index: ComponentIndex, root: Path, backbone: nn.Module,
                     *, batch_size: int) -> torch.Tensor:
    """Independent fixed transform per index image; no state fitted on other splits."""
    if not index.components or not 1 <= batch_size <= 128:
        raise ValueError("empty index or invalid feature batch size")
    if any(parameter.requires_grad for parameter in backbone.parameters()):
        raise ValueError("backbone must be frozen")
    backbone.eval()  # Includes frozen BatchNorm buffers and disables dropout.
    before = tensor_hash(backbone.state_dict())
    batches = []
    with torch.inference_mode():
        for offset in range(0, len(index.components), batch_size):
            subset = index.components[offset:offset + batch_size]
            inputs = torch.from_numpy(np.stack([preprocess(load_rgb(root, item.row)) for item in subset]))
            output = backbone(inputs).cpu()
            if output.ndim != 2 or output.shape[0] != len(subset) or not torch.isfinite(output).all():
                raise ValueError("backbone produced invalid features")
            batches.append(output)
    if tensor_hash(backbone.state_dict()) != before:
        raise ValueError("frozen backbone changed during feature extraction")
    # Clone outside inference_mode to allow autograd for the head.
    return torch.cat(batches).clone()


class FeatureHead(nn.Module):
    def __init__(self, mean: torch.Tensor, scale: torch.Tensor):
        super().__init__()
        self.register_buffer("mean", mean.detach().clone())
        self.register_buffer("scale", scale.detach().clone())
        self.linear = nn.Linear(len(mean), 1)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.linear((features - self.mean) / self.scale).squeeze(-1)


class Baseline(nn.Module):
    """One raw binary logit; scoring layer applies temperature/sigmoid once."""
    notice = PLACEHOLDER_NOTICE

    def __init__(self, backbone: nn.Module, head: FeatureHead):
        super().__init__()
        self.backbone, self.head = backbone, head

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.head(self.backbone(inputs))


def fit_head(index: ComponentIndex, features: torch.Tensor,
             config: TrainingConfig) -> tuple[FeatureHead, dict]:
    """Feature scaling and fixed-epoch optimisation see training components only."""
    if (features.ndim != 2 or features.shape[0] != len(index.components)
            or features.shape[1] < 1 or features.device.type != "cpu"
            or features.dtype != torch.float32 or not torch.isfinite(features).all()):
        raise ValueError("invalid component feature matrix")
    positions = [i for i, item in enumerate(index.components) if item.split == "train"]
    targets = torch.tensor([index.components[i].target for i in positions], dtype=torch.float32)
    if set(targets.tolist()) != {0.0, 1.0}:
        raise ValueError("training needs both synthetic classes")
    initialise(config)
    inputs = features[positions].detach().clone()
    mean = inputs.mean(0)
    std = inputs.std(0, correction=0)
    scale = torch.where(std < 1e-6, torch.ones_like(std), std)
    head = FeatureHead(mean, scale)
    optimizer = torch.optim.AdamW(head.parameters(), lr=config.learning_rate,
                                 weight_decay=config.weight_decay)
    losses = []
    for _ in range(config.epochs):
        optimizer.zero_grad(set_to_none=True)
        loss = nn.functional.binary_cross_entropy_with_logits(head(inputs), targets)
        if not torch.isfinite(loss):
            raise ValueError("non-finite training loss")
        losses.append(float(loss.detach()))
        loss.backward()
        optimizer.step()
    head.eval()
    with torch.inference_mode():
        final_loss = float(nn.functional.binary_cross_entropy_with_logits(head(inputs), targets))
    if not np.isfinite(final_loss) or not all(torch.isfinite(v).all() for v in head.state_dict().values()):
        raise ValueError("non-finite trained head")
    training_ids = [index.components[i].id for i in positions]
    return head, {"notice": PLACEHOLDER_NOTICE, "config": asdict(config),
                  "fit_split": "train", "components": len(positions),
                  "target_counts": {str(t): int((targets == t).sum()) for t in (0, 1)},
                  "component_ids_sha256": hashlib.sha256(json.dumps(sorted(training_ids)).encode()).hexdigest(),
                  "training_features_sha256": tensor_hash({"features": inputs}),
                  "feature_scaling": "train-only population std; std<1e-6 replaced by 1",
                  "feature_scaling_sha256": tensor_hash({"mean": mean, "scale": scale}),
                  "optimizer": "full-batch AdamW, fixed epochs, no early stopping/search",
                  "metadata_fusion": False, "loss_before_updates": losses[0],
                  "loss_after_updates": final_loss, "head_sha256": tensor_hash(head.state_dict())}


def predict(index: ComponentIndex, features: torch.Tensor, head: FeatureHead):
    with torch.inference_mode():
        scores = head(features).tolist()
    return component_predictions(index, {item.id: score for item, score in zip(index.components, scores, strict=True)})
