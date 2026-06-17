#!/bin/bash

# หา path ของ flet web directory
FLET_WEB=$(python3 -c "import flet; import os; print(os.path.join(os.path.dirname(flet.__file__), 'web'))")

echo "==> Flet web dir: $FLET_WEB"
echo "==> Replacing icons..."

# แทนที่ favicon
cp assets/favicon.png "$FLET_WEB/favicon.png" && echo "✓ favicon.png replaced"

# แทนที่ icons สำหรับ splash/loading screen
cp assets/icons/icon-192.png "$FLET_WEB/icons/icon-192.png" && echo "✓ icon-192.png replaced"
cp assets/icons/icon-512.png "$FLET_WEB/icons/icon-512.png" && echo "✓ icon-512.png replaced"

echo "==> Starting app..."
python3 puifai-comparason.py
