import os
import sys
import shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.config import DATA_DIR
from pipeline.utils import setup_logger

logger = setup_logger("ExportToUI")

def export_data():
    """Copies all analysis artifacts to the Next.js public folder for serving."""
    ui_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui", "public", "data")
    
    # Create target directories
    os.makedirs(os.path.join(ui_data_dir, "aggregates"), exist_ok=True)
    os.makedirs(os.path.join(ui_data_dir, "clusters"), exist_ok=True)
    os.makedirs(os.path.join(ui_data_dir, "audit"), exist_ok=True)
    os.makedirs(os.path.join(ui_data_dir, "index"), exist_ok=True)
    
    # Define source directories
    sources = {
        "aggregates": DATA_DIR / "aggregates",
        "clusters": DATA_DIR / "clusters",
        "audit": DATA_DIR / "audit",
        "index": DATA_DIR / "index",
    }
    
    copied = 0
    for name, src_dir in sources.items():
        if src_dir.exists():
            for filename in os.listdir(src_dir):
                if filename.endswith(".json") or filename.endswith(".html"):
                    src_file = src_dir / filename
                    dst_file = os.path.join(ui_data_dir, name, filename)
                    shutil.copy2(src_file, dst_file)
                    copied += 1
                    
    logger.info(f"Copied {copied} files to {ui_data_dir}. The frontend is now connected to the backend data.")

if __name__ == "__main__":
    export_data()
