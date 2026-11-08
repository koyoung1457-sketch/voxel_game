# 복셀 게임 프로그램 구조 설명서

> 이 문서는 2026-11-08 대화에 첨부된 Python 파일을 기준으로 작성했다.
> 코드에서 확인되는 현재 구조와, 아직 구현되지 않았거나 수정이 필요한
> 부분을 구분했다.

## 1. 프로그램 한눈에 보기

이 프로그램은 **Pygame으로 입력과 게임 루프를 관리하고, PyOpenGL로 3D
장면을 렌더링하는 복셀 게임**이다.

-   플레이어가 WASD와 마우스로 이동·시선을 조작한다.
-   월드에는 정수 좌표를 중심으로 하는 블록이 저장된다.
-   레이캐스트로 바라보는 블록을 찾고, 마우스 클릭으로 블록을 파괴하거나
    설치한다.
-   파괴된 블록은 작은 물리 엔티티로 생성된다.
-   OpenGL이 블록과 엔티티를 화면에 그린다.
-   UI는 별도의 Pygame Surface에 그리는 구조로 작성되어 있지만, 현재
    `main.py`의 `screen.blit()`는 OpenGL 디스플레이와 맞지 않아 그대로는
    정상적인 UI 출력 방식이 아니다.

## 2. 파일 구성

``` text
project/
│
├── main.py          # 프로그램 시작점, 초기화, 게임 루프
│
├── player.py        # 플레이어 상태, 이동, 중력, 충돌, 인벤토리
├── camera.py        # 카메라의 시선 방향과 FOV 설정값
├── world.py         # 월드의 블록 데이터 관리
├── entity.py        # 파괴된 블록 조각 엔티티
│
├── raycast.py       # 플레이어 시선으로 블록 탐색
├── rect3.py         # 3차원 충돌 상자와 충돌 판정
├── math3.py         # 카메라 기준 좌표 변환 등의 수학 함수
│
├── rendering.py     # OpenGL을 이용한 3D 렌더링
├── texture.py       # 이미지 파일을 OpenGL 텍스처로 등록·조회
├── blocks.py        # 블록 종류와 텍스처 파일 경로 정의
├── UI.py            # Pygame Surface 기반 UI 그리기
│
└── textures/        # 블록 텍스처 이미지 파일
```

첨부된 파일에서 확인한 모듈을 기준으로 정리했다. 실제 폴더에 다른 파일이
더 있을 수 있다.

## 3. 전체 의존 관계

화살표는 대체로 "왼쪽 모듈이 오른쪽 모듈을 가져다 쓰거나 호출한다"는
뜻이다.

``` text
                         main.py
                ┌──────────┼─────────────┐
                │          │             │
                ▼          ▼             ▼
             player.py   world.py    rendering.py
                │                        │
                ▼                        ├──────────► math3.py
             camera.py                   │
                │                        └──────────► texture.py
                ▼                                      │
             rect3.py                                  ▼
                ▲                                   blocks.py
                │
             entity.py

main.py ───────► raycast.py ───────► world.py
   │
   ├───────────► rect3.py
   │
   └───────────► UI.py
```

추가 관계: - `player.py`는 `camera.py`와 `rect3.py`를 사용한다. -
`entity.py`는 `rect3.py`를 사용한다. - `rendering.py`는 `math3.py`로
월드 좌표를 카메라 기준 좌표로 바꾸고, `texture.py`에서 텍스처 ID를
얻는다. - `texture.py`는 `blocks.py`에 정의된 텍스처 경로를 읽는다. -
`raycast.py`는 `world.py`의 `has()`를 사용해 블록이 있는지 확인한다.

## 4. 각 파일의 역할

### 4.1 `main.py` --- 전체 진행을 지휘하는 곳

`main.py`는 게임의 시작점이다. 다른 모듈의 객체를 만들고, 매 프레임마다
입력 처리·물리 업데이트·렌더링을 실행한다.

초기화 순서:

1.  Pygame을 초기화한다.
2.  OpenGL 옵션으로 창을 만든다.
3.  OpenGL 컨텍스트가 만들어진 뒤 `texture.load_all_textures()`를
    호출한다.
4.  `Player`, `World`, `Rendering`, `UI` 객체와 엔티티 목록을 만든다.
5.  카메라 FOV에 맞춰 투영 설정을 한다.
6.  테스트용 흙 블록을 월드에 배치한다.
7.  플레이어의 스폰 위치를 정한다.

주요 변수:

  변수         의미
  ------------ ------------------------------------------
  `screen`     OpenGL 창. 일반 Pygame Surface와 다르다.
  `player`     플레이어 객체
  `world`      블록 데이터가 들어 있는 월드
  `entities`   파괴되어 떨어지는 블록 조각 목록
  `render`     OpenGL 렌더러
  `ui`         UI 그리기 객체
  `clock`      프레임 시간 계산용 시계
  `dt`         직전 프레임에 걸린 시간(초)

게임 루프의 흐름:

``` text
프레임 시작
   │
   ├─ dt 계산
   ├─ 키보드/마우스 이벤트 처리
   │    ├─ ESC: 게임 종료
   │    ├─ 왼쪽 클릭: 바라보는 블록 파괴
   │    └─ 오른쪽 클릭: 인벤토리 블록 설치
   │
   ├─ 현재 눌린 키 확인
   ├─ player.move()       입력에 따른 속도와 카메라 회전
   ├─ player.update()     중력과 충돌 처리
   ├─ entity.update()     떨어지는 블록 조각의 물리 처리
   ├─ 엔티티 제거 조건 확인
   ├─ 플레이어 낙하/재스폰 확인
   ├─ 레이캐스트로 바라보는 블록 확인
   │
   ├─ render.begin_frame()
   ├─ render.painters_algorithm()  월드와 엔티티 렌더링
   ├─ render.draw_block_wireframe() 바라보는 블록 테두리
   ├─ UI 그리기
   └─ pygame.display.flip() 화면 표시
```

현재 첨부된 `main.py`에는 `render.draw_crosshair()` 호출이 있고, UI 출력
부분에는 `screen.blit(...)`가 있다. OpenGL 창에서는 일반 Pygame
디스플레이처럼 `screen.blit()`로 그릴 수 없으므로, UI Surface를 OpenGL
텍스처로 표시하는 별도 렌더링 함수가 필요하다. 십자선을 UI Surface에
넣는 방식으로 바꾼다면 `draw_crosshair()`는 더 이상 호출하지 않도록
정리하면 된다.

### 4.2 `player.py` --- 플레이어

`Player` 클래스는 플레이어의 상태와 행동을 관리한다.

주요 데이터:

  속성               의미
  ------------------ -------------------------
  `rect`             플레이어의 충돌 상자
  `vx`, `vy`, `vz`   각 축 방향 속도
  `speed`            수평 이동 속도
  `gravity`          중력 가속도 크기
  `jump_speed`       점프 초기 속도
  `on_ground`        땅에 닿아 있는지 여부
  `camera`           카메라 객체
  `inventory`        9칸 인벤토리
  `inventory_idx`    현재 선택한 인벤토리 칸
  `hp`               체력
  `spawn_pos`        기본 스폰 위치

주요 메서드:

-   `move(key, screen)`: WASD 입력으로 수평 속도를 정하고, 마우스
    이동량으로 카메라 yaw/pitch를 바꾼다. 숫자 1\~9로 인벤토리 칸을
    선택하고 스페이스로 점프한다.
-   `update(world, dt)`: 중력과 이동을 적용하고 월드 블록과 충돌하는지
    검사한다. X, Z, Y축을 나누어 처리한다.
-   `_collides(world, x, y, z)`: 특정 위치에 플레이어를 놓았을 때 블록과
    겹치는지 검사한다.
-   `find_free_spawn(world)`: 스폰 지점 주변에서 블록과 겹치지 않는
    위치를 찾는다.
-   `spawn(world, keep_inventory)`: 플레이어 위치와 속도를 초기화한다.
-   `discount()`: 현재 선택된 블록의 수량을 1 줄인다.
-   `now_block`: 현재 선택된 블록 종류를 반환하는 프로퍼티.

`x`, `y`, `z`는 `rect`의 좌표를 가져오는 프로퍼티다. `cx`, `cy`, `cz`는
카메라/시선 계산에 사용하는 위치이며, `cy`는 플레이어의 `y`에 1.4를
더한다.

### 4.3 `camera.py` --- 카메라 설정값

`Camera` 클래스는 카메라의 설정값을 보관한다.

-   `yaw`: 좌우 회전 각도
-   `pitch`: 위아래 회전 각도
-   `sensitive`: 마우스 감도
-   `fov`: 시야각(Field of View)
-   `x`, `y`, `z`: 카메라 좌표로 정의되어 있지만, 첨부된 코드에서는
    플레이어의 `cx`, `cy`, `cz`가 렌더링과 레이캐스트에 전달된다.

실제 이동과 회전 계산은 `player.py`에서 수행하고, 카메라는 각도와
설정값을 보관하는 역할을 한다.

### 4.4 `world.py` --- 블록 데이터

`World`는 블록의 위치와 종류를 저장한다.

-   `blocks`: 블록 좌표를 담는 집합(set)
-   `blocks2`: 좌표를 블록 종류에 연결하는 딕셔너리

예를 들어 `(1, 0, 2)` 위치에 흙 블록이 있다면: - `blocks`에는
`(1, 0, 2)`가 들어간다. - `blocks2[(1, 0, 2)]`는 `"dirt"`다.

메서드:

-   `add(pos, kind)`: 블록 추가
-   `remove(pos)`: 블록 좌표를 집합에서 제거
-   `has(pos)`: 해당 좌표에 블록이 있는지 확인
-   `get_kind(pos)`: 해당 좌표의 블록 종류 반환

**주의:** 현재 `remove()`는 `blocks`에서는 좌표를 제거하지만
`blocks2`에서는 키를 삭제하지 않는다. 당장 `has()`가 거짓이면 렌더러가
순회하지 않지만, 오래된 종류 데이터가 딕셔너리에 남는다. 데이터 정합성을
위해 나중에 `blocks2.pop(pos, None)`도 수행하도록 개선할 수 있다.

### 4.5 `entity.py` --- 떨어지는 블록 조각

`Block` 클래스는 블록을 부쉈을 때 생성되는 작은 블록 엔티티를 표현한다.

-   일반 블록보다 작은 충돌 상자를 가진다.
-   `kind`로 원래 블록 종류를 기억한다.
-   `vx`, `vy`, `vz` 속도를 가진다.
-   중력의 영향을 받는다.
-   월드 블록과 충돌하면 멈추거나 위치를 보정한다.
-   `faces`는 렌더링할 6개 면의 정점 인덱스와 면 종류를 제공한다.
-   `verticals`는 작은 큐브의 8개 꼭짓점 좌표를 제공한다.

물리 업데이트 방식은 플레이어와 비슷하지만, 현재 엔티티에는 플레이어의
인벤토리나 체력 기능은 없다.

### 4.6 `raycast.py` --- 바라보는 블록 찾기

`raycast()`는 플레이어의 시선 방향으로 가상의 광선을 쏴서 가장 먼저
만나는 블록을 찾는다.

입력: - 카메라 위치 `cx`, `cy`, `cz` - 시선 각도 `yaw`, `pitch` -
`world` - 최대 탐색 거리 `max_dist`

내부에서는 yaw와 pitch로 시선 방향 벡터를 계산하고, DDA 방식으로 복셀
격자를 한 칸씩 탐색한다.

반환값: - `hit_block`: 맞은 블록 좌표 - `place_block`: 맞은 면의 바깥쪽,
새 블록을 놓을 좌표 - 맞은 블록이 없으면 `(None, None)`

`main.py`는 이 결과를 사용해 왼쪽 클릭 시 블록을 제거하고, 오른쪽 클릭
시 인벤토리의 블록을 설치한다. 매 프레임 호출해 현재 바라보는 블록을
표시하는 데도 사용한다.

### 4.7 `rect3.py` --- 3차원 충돌 상자

이 파일은 3차원 직육면체의 크기·위치·충돌 판정을 계산한다.

-   `BlockRect`: 블록의 중심을 기준으로 크기를 갖는 상자
-   `EntityRect`: 엔티티의 위치를 기준으로 상자를 정의하며, 아래쪽
    기준이 `BlockRect`와 다르다.
-   `block_rect(block)`: 블록 좌표를 1×1×1 충돌 상자로 바꾼다.

`colliderect()`는 X, Y, Z 세 축에서 두 상자가 겹치는지 검사한다. 세 축
모두 겹쳐야 3차원 충돌로 판단한다.

### 4.8 `math3.py` --- 좌표 계산

현재 코드에서 중요한 함수는 `world_to_screen()`이다.

이름은 화면 좌표를 반환하는 것처럼 보이지만, 실제로는: 1. 월드 좌표에서
카메라 위치를 뺀다. 2. yaw 회전을 적용한다. 3. pitch 회전을 적용한다. 4.
카메라 기준의 `(x, y, z)` 좌표를 반환한다.

이 좌표를 `rendering.py`가 OpenGL 정점으로 전달한다. 코드 주석에 따르면
이 함수의 카메라 앞 방향은 `+z`이고, OpenGL 기본 카메라의 앞 방향은
`-z`이므로 렌더러에서 z 부호를 반대로 전달한다.

파일에는 원근 투영 `project()`와 삼각형의 무게중심 좌표를 계산하는
`barycentric()`도 정의되어 있지만, 첨부된 현재 렌더러 경로에서
핵심적으로 호출되는 함수는 `world_to_screen()`이다.

### 4.9 `rendering.py` --- OpenGL 렌더러

`Rendering` 클래스는 3D 월드와 엔티티를 화면에 그린다.

주요 메서드:

-   `__init__(width, height)`: 화면 크기를 저장하고 깊이 테스트와
    배경색을 설정한다.
-   `set_projection(fov)`: 원근 투영 행렬을 설정한다.
-   `begin_frame()`: 색상 버퍼와 깊이 버퍼를 지운다.
-   `painters_algorithm(...)`: 월드 블록과 엔티티를 순회하며 렌더링한다.
    이름은 painters algorithm이지만 실제 깊이 처리는 OpenGL의 Z-buffer가
    한다.
-   `_draw_face(...)`: 블록의 한 면을 정점과 텍스처로 그린다.
-   `_draw_entity_face(...)`: 엔티티의 한 면을 그린다.
-   `draw_block_wireframe(...)`: 현재 바라보는 블록 주위에
    와이어프레임을 그린다.
-   `draw_crosshair()`: 현재 파일에는 십자선을 OpenGL 선으로 직접 그리는
    함수가 있다.

`FACE_DEFS`는 블록의 여섯 방향 면을 정의하고, `FACE_UV`는 각 면의 텍스처
좌표 순서를 정의한다. 이웃한 블록이 이미 차지하고 있는 면은 그리지 않아
불필요한 면 렌더링을 줄인다.

### 4.10 `texture.py` --- 텍스처 관리

이 모듈은 Pygame 이미지 Surface를 OpenGL 텍스처로 변환하고, 블록 종류와
면에 맞는 텍스처 ID를 찾아준다.

핵심 개념: - 텍스처 파일 경로를 읽는다. - 이미지를 OpenGL이 사용할 수
있는 텍스처로 등록한다. - 블록 종류와 면 이름으로 텍스처를 조회한다. -
이미지가 없으면 기본 누락 텍스처를 대신 사용한다. - 블록용 텍스처와
엔티티용 텍스처 캐시를 따로 관리한다.

주요 함수: - `_surface_to_gl_texture(surface)`: Pygame Surface를 OpenGL
텍스처로 등록한다. - `_load_gl_texture(path)`: 파일을 읽어 텍스처로
만든다. - `_load_default_texture()`: 기본 누락 텍스처를 준비한다. -
`load_all_textures()`: 등록된 블록/엔티티 텍스처를 한 번에 불러온다. -
`get_texture(kind, face, entity=False)`: 종류와 면에 맞는 텍스처 ID를
반환한다.

OpenGL 텍스처를 만들려면 OpenGL 컨텍스트가 먼저 존재해야 하므로,
`main.py`에서 창을 만든 다음 `load_all_textures()`를 호출한다.

### 4.11 `blocks.py` --- 블록 종류와 이미지 연결

이 파일은 블록의 종류와 텍스처 파일 경로를 모아 둔다.

현재 블록 종류: - `dirt` - `grass` - `stone` - `oak_log`

`BLOCK_TEXTURES`는 일반 블록 렌더링에 사용할 이미지 경로를 정의한다.
`ENTITY_TEXTURES`는 떨어지는 블록 엔티티에 사용할 이미지 경로를
정의한다.

예를 들어 잔디 블록은 윗면에 `grass_top.png`, 옆면에 `grass_side.png`,
아랫면에 흙 텍스처를 사용한다.

### 4.12 `UI.py` --- 화면 UI

`UI` 클래스는 Pygame Surface에 2D 요소를 그리는 역할을 맡도록 작성되어
있다.

-   `__init__`: 화면 크기의 Surface 생성
-   `update`: 현재는 비어 있음
-   `draw(inventory, hp)`: UI를 Surface에 그리고 그 Surface를 반환

현재 파일은 화면 아래쪽에 흰색 사각형 하나를 그리는 수준이다.
`inventory`와 `hp` 인자를 받지만 아직 실제로 그리는 코드는 없다.

UI를 OpenGL 창에 표시하려면 일반 `screen.blit()` 대신 다음과 같은 연결이
필요하다.

``` text
UI.draw()
   │
   ▼
Pygame Surface
   │
   ▼
Surface 픽셀 데이터를 OpenGL 텍스처로 전달
   │
   ▼
OpenGL의 2D 사각형에 텍스처 표시
```

십자선도 UI에 넣기로 한다면 `UI.draw()` 안에서 `pygame.draw.line()`
등으로 그릴 수 있다. 그 경우 기존 `render.draw_crosshair()` 호출은
제거해야 한다.

## 5. 실제 게임 동작 흐름

### 5.1 플레이어 이동

``` text
키보드 입력
   │
   ▼
Player.move()
   ├─ WASD → vx, vz 계산
   ├─ Space → 점프 속도 설정
   ├─ 마우스 → camera.yaw / pitch 변경
   └─ 숫자 1~9 → inventory_idx 변경
   │
   ▼
Player.update(world, dt)
   ├─ 중력 적용
   ├─ X축 이동 및 충돌 보정
   ├─ Z축 이동 및 충돌 보정
   └─ Y축 이동 및 충돌 보정
```

### 5.2 블록 파괴

``` text
마우스 왼쪽 클릭
   │
   ▼
raycast(...)
   │
   ├─ 맞은 블록이 없음 → 아무것도 하지 않음
   │
   └─ 맞은 블록이 있음
         │
         ├─ Entity.Block 생성
         └─ world.remove(hit)
```

### 5.3 블록 설치

``` text
마우스 오른쪽 클릭
   │
   ▼
raycast(...)
   │
   ▼
설치할 위치(place) 계산
   │
   ├─ 이미 블록이 있음 → 설치하지 않음
   │
   └─ 빈 위치이고 선택 칸에 블록이 있음
         │
         ├─ world.add(place, player.now_block)
         ├─ 플레이어와 겹치는지 검사
         └─ 겹치지 않으면 player.discount()
```

### 5.4 화면 렌더링

``` text
render.begin_frame()
   │
   ▼
화면 버퍼 초기화
   │
   ▼
render.painters_algorithm(...)
   ├─ 월드 블록 순회
   ├─ 가려진 면 생략
   ├─ texture.get_texture()로 텍스처 조회
   ├─ 블록 면 그리기
   └─ 엔티티 면 그리기
   │
   ▼
render.draw_block_wireframe(...)
   │
   ▼
UI Surface를 OpenGL로 표시
   │
   ▼
pygame.display.flip()
```

## 6. 알아두면 좋은 핵심 개념

  -----------------------------------------------------------------------
  개념                                이 프로젝트에서의 의미
  ----------------------------------- -----------------------------------
  월드 좌표                           블록과 플레이어가 게임 세계에서
                                      차지하는 위치

  카메라 좌표                         카메라를 기준으로 변환한 좌표

  yaw                                 좌우 시선 회전

  pitch                               위아래 시선 회전

  FOV                                 카메라가 한 번에 볼 수 있는 시야각

  충돌 상자                           물체가 서로 겹치는지 계산하기 위한
                                      직육면체

  레이캐스트                          시선 방향으로 공간을 탐색해 블록을
                                      찾는 방법

  DDA                                 격자 공간을 한 칸씩 효율적으로
                                      탐색하는 알고리즘

  텍스처                              블록 표면에 입히는 이미지

  Z-buffer                            픽셀마다 깊이를 저장해 앞에 있는
                                      물체가 뒤의 물체를 가리도록 하는
                                      기능

  Surface                             Pygame에서 2D 픽셀 이미지를 담는
                                      객체

  OpenGL 텍스처                       GPU가 사용할 수 있도록 등록한
                                      이미지 데이터
  -----------------------------------------------------------------------

## 7. 현재 코드에서 확인되는 주의 사항

1.  **UI 출력:** 현재 `main.py`의 `screen`은 `OPENGL` 옵션으로 생성됐다.
    따라서 일반 Pygame Surface처럼 `screen.blit()`를 호출하는 구조는
    맞지 않는다. UI Surface를 OpenGL 텍스처로 표시하는 과정이 필요하다.
2.  **십자선 중복:** 현재는 `render.draw_crosshair()`가 OpenGL로
    십자선을 그린다. 십자선을 `UI.py`로 옮기면 기존 호출을 제거해야
    한다.
3.  **월드 블록 삭제:** `World.remove()`는 현재 `blocks`에서만 제거한다.
    `blocks2`에서도 삭제하도록 개선할 수 있다.
4.  **인벤토리 빈 칸:** `Player.now_block`은 현재 선택 칸이 `None`일 때
    접근하면 오류가 날 수 있다. 설치 코드처럼 사용 전에 빈 칸인지
    검사해야 한다.
5.  **엔티티 목록 변경:** `main.py`는 `for entity in entities` 순회 중
    해당 엔티티를 리스트에서 제거한다. 이런 방식은 다음 항목을 건너뛸 수
    있으므로, 나중에 제거할 대상을 별도로 모으거나 새 리스트를 만드는
    방식으로 개선할 수 있다.
6.  **현재 문서의 범위:** 이 설명서는 첨부된 소스 코드에서 확인한 동작을
    정리한 것이다. 아직 첨부되지 않은 모듈이나 향후 구현할 기능은
    포함하지 않았다.

## 8. 코드를 읽을 때 추천하는 순서

처음부터 모든 수학과 OpenGL 코드를 이해하려고 하면 부담이 크다. 다음
순서로 읽으면 전체 흐름을 잡기 쉽다.

1.  `main.py` --- 프로그램이 어떤 순서로 움직이는지 파악
2.  `world.py` --- 블록 데이터가 어떻게 저장되는지 파악
3.  `player.py` --- 입력, 이동, 중력, 충돌 파악
4.  `rect3.py` --- 충돌 판정 원리 파악
5.  `raycast.py` --- 블록을 어떻게 선택하는지 파악
6.  `entity.py` --- 부서진 블록 조각이 어떻게 움직이는지 파악
7.  `camera.py`, `math3.py` --- 시선과 좌표 변환 파악
8.  `blocks.py`, `texture.py` --- 이미지가 텍스처가 되는 과정 파악
9.  `rendering.py` --- 최종적으로 3D 화면을 그리는 과정 파악
10. `UI.py` --- 2D 화면 요소를 구성하고 OpenGL 화면에 연결하는 과정 파악

**전체를 한 문장으로 요약하면:** `main.py`가 게임의 진행을 지휘하고,
`player.py`·`world.py`·`entity.py`가 게임 상태를 관리하며,
`raycast.py`와 `rect3.py`가 상호작용을 계산하고, `rendering.py`와
`texture.py`가 그 결과를 화면에 보여준다.
