#!/bin/zsh
cd "${0:A:h}" || exit 1
if [[ ! -x .venv/bin/python || ! -f examples/steamship_scene.blend ]]; then
  python3 scripts/setup.py || { read '?安装未完成，按回车关闭'; exit 1; }
fi
.venv/bin/python scripts/launch.py
