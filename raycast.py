import math

def raycast(cx, cy, cz, yaw, pitch, world, max_dist=12.0):
    # 1. 시선 방향 벡터 구하기
    dx = math.sin(yaw) * math.cos(pitch)
    dy = math.sin(pitch)
    dz = math.cos(yaw) * math.cos(pitch)

    # 안전장치: 방향 벡터가 0인 축은 아주 미세한 값을 더해 ZeroDivisionError 및 Inf 오차 예방
    dx = dx if dx != 0 else 1e-9
    dy = dy if dy != 0 else 1e-9
    dz = dz if dz != 0 else 1e-9

    # 2. 블록 경계가 정수 0.5 단위를 가지므로,
    # 좌표계를 전체적으로 0.5만큼 더해 완벽한 정수 격자계(Integer Grid)로 변환합니다.
    # 이렇게 하면 경계선이 정확히 정수(1.0, 2.0, 3.0 ...) 상에 놓여 연산 오차가 사라집니다.
    rx = cx + 0.5
    ry = cy + 0.5
    rz = cz + 0.5

    # 현재 플레이어가 위치한 정수 복셀(Grid) 좌표
    map_x = int(math.floor(rx))
    map_y = int(math.floor(ry))
    map_z = int(math.floor(rz))

    # 각 축 방향으로 격자 1칸을 전진하기 위해 필요한 레이의 누적 길이 비율
    delta_x = abs(1 / dx)
    delta_y = abs(1 / dy)
    delta_z = abs(1 / dz)

    # 초기 전진 거리(side_dist) 및 방향(step) 설정
    if dx < 0:
        step_x = -1
        side_dist_x = (rx - map_x) * delta_x
    else:
        step_x = 1
        side_dist_x = (map_x + 1.0 - rx) * delta_x

    if dy < 0:
        step_y = -1
        side_dist_y = (ry - map_y) * delta_y
    else:
        step_y = 1
        side_dist_y = (map_y + 1.0 - ry) * delta_y

    if dz < 0:
        step_z = -1
        side_dist_z = (rz - map_z) * delta_z
    else:
        step_z = 1
        side_dist_z = (map_z + 1.0 - rz) * delta_z

    hit_block = None
    normal = (0, 0, 0)
    distance = 0.0

    # 3. DDA 루프 실행 (최대 거리 안에서 정수 격자를 한 칸씩 추적)
    while distance < max_dist:
        # X, Y, Z 격자선 중 가장 먼저 만나는 면을 선택하여 이동
        if side_dist_x < side_dist_y and side_dist_x < side_dist_z:
            distance = side_dist_x
            side_dist_x += delta_x
            map_x += step_x
            normal = (-step_x, 0, 0) # 레이가 들어온 방향의 반대 면(즉, 충돌면) 법선 벡터
        elif side_dist_y < side_dist_z:
            distance = side_dist_y
            side_dist_y += delta_y
            map_y += step_y
            normal = (0, -step_y, 0)
        else:
            distance = side_dist_z
            side_dist_z += delta_z
            map_z += step_z
            normal = (0, 0, -step_z)

        # 검사 좌표를 다시 원래 월드 좌표계(0.5를 뺀 값)로 매핑하여 블록 존재 여부 확인
        target = (map_x, map_y, map_z)
        if world.has(target):
            hit_block = target
            break

    if hit_block:
        # 충돌한 블록 면 방향으로 1칸 더한 좌표 계산
        place_block = (hit_block[0] + normal[0], hit_block[1] + normal[1], hit_block[2] + normal[2])
        return hit_block, place_block

    return None, None