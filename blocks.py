BLOCKS = {"dirt", "grass", "stone", "oak_log"}

DIRT = "textures/dirt.png"
GRASS_TOP = "textures/grass_top.png"
GRASS_SIDE = "textures/grass_side.png"
STONE = "textures/stone.png"
OAK_LOG_TOP = "textures/oak_log_top.png"
OAK_LOG_SIDE = "textures/oak_log.png"


BLOCK_TEXTURES = {
    "dirt": {
        "all": DIRT,
    },
    "grass": {
        "top": GRASS_TOP,
        "side": GRASS_SIDE,
        "bottom": DIRT,
    },
    "stone": {
        "all": STONE,
    },
    "oak_log": {
        "top": OAK_LOG_TOP,
        "side": OAK_LOG_SIDE,
        "bottom": OAK_LOG_TOP
    }
}

ENTITY_TEXTURES = {
    "dirt": {
        "all": DIRT,
    },
    "grass": {
        "top": GRASS_TOP,
        "side": GRASS_SIDE,
        "bottom": DIRT,
    },
    "stone": {
        "all": STONE,
    },
    "oak_log": {
        "top": OAK_LOG_TOP,
        "side": OAK_LOG_SIDE,
        "bottom": OAK_LOG_TOP
    }
}

ITEM_TEXTURE = {
    "dirt": {
        DIRT
    },
    "grass": {
        GRASS_SIDE
    },
    "stone": {
        STONE
    },
    "oak_log": {
        OAK_LOG_TOP
    }
}