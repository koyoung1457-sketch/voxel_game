여기에 텍스처 이미지(.png)를 넣으세요.
blocks.py의 BLOCK_TEXTURES에 적힌 파일명과 정확히 같아야 합니다.

예시:
  textures/dirt.png        (흙 - 모든 면 공용)
  textures/stone.png       (돌 - 모든 면 공용)
  textures/grass_top.png   (잔디 윗면)
  textures/grass_side.png  (잔디 옆면)
  # 잔디 아랫면은 dirt.png를 그대로 재사용하도록 이미 설정되어 있습니다.

이미지가 없는 종류는 자동으로 누락 텍스처(체크무늬)로 대체되어 그려집니다.

[누락 텍스처 안내]
특정 블록/면의 이미지 파일이 없으면 이제 단색이 아니라
"누락 텍스처" 이미지로 대체됩니다.
- textures/missing.png 파일을 직접 만들어두면 그 이미지가 쓰이고,
- 없으면 자동으로 보라/검정 체크무늬가 생성되어 대신 쓰입니다.
