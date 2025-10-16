#!/bin/bash
# 🚀 Flatten MyTriv ERP repo structure and push to GitHub

set -e

# 1️⃣ Pastikan branch main terbaru
git checkout main
git pull origin main

# 2️⃣ Buat branch baru untuk flatten
BRANCH_NAME="flatten-github"
git checkout -b $BRANCH_NAME

# 3️⃣ Pindahkan semua folder dan file dari nested folder ke root
NESTED_FOLDER="mytriv-erp"  # ganti sesuai folder nested yang muncul di GitHub
if [ -d "$NESTED_FOLDER" ]; then
    echo "📦 Moving files from $NESTED_FOLDER to root..."
    shopt -s dotglob  # termasuk file hidden
    mv $NESTED_FOLDER/* .
    shopt -u dotglob
    rmdir $NESTED_FOLDER
else
    echo "✅ No nested folder found, skipping move."
fi

# 4️⃣ Tambahkan semua perubahan ke git
git add .

# 5️⃣ Commit perubahan
git commit -m "🧹 Flatten folder structure: move all files to root"

# 6️⃣ Push branch baru ke GitHub
git push -u origin $BRANCH_NAME

echo "🎉 Branch '$BRANCH_NAME' pushed. Create a Pull Request on GitHub to merge into main."
