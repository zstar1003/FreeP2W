from PIL import Image
from surya.foundation import FoundationPredictor
from surya.layout import LayoutPredictor
from surya.settings import settings

image = Image.open(IMAGE_PATH)
layout_predictor = LayoutPredictor(FoundationPredictor(checkpoint=settings.LAYOUT_MODEL_CHECKPOINT))

# layout_predictions is a list of dicts, one per image
layout_predictions = layout_predictor([image])