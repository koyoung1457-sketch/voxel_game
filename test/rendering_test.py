import pygame
from pygame.locals import *

from OpenGL.GL import *
import numpy as np

pygame.init()

pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_MAJOR_VERSION, 3
)
pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_MINOR_VERSION, 3
)
pygame.display.gl_set_attribute(
    pygame.GL_CONTEXT_PROFILE_MASK,
    pygame.GL_CONTEXT_PROFILE_CORE
)

pygame.display.set_mode(
    (800, 600),
    pygame.OPENGL | pygame.DOUBLEBUF
)

print("OpenGL:", glGetString(GL_VERSION))
print("GLSL:", glGetString(GL_SHADING_LANGUAGE_VERSION))

vertices = [
    # 앞면
    -1, -1,  1,
     1, -1,  1,
     1,  1,  1,
    -1,  1,  1,

    # 뒷면
    -1, -1, -1,
     1, -1, -1,
     1,  1, -1,
    -1,  1, -1,
]


vbo = glGenBuffers(1)

glBindBuffer(GL_ARRAY_BUFFER, vbo)

glBufferData(
    GL_ARRAY_BUFFER,
    vertices.nbytes,
    vertices,
    GL_STATIC_DRAW
)


vao = glGenVertexArrays(1)

glBindVertexArray(vao)

glBindBuffer(GL_ARRAY_BUFFER, vbo)

glVertexAttribPointer(
    0,
    3,
    GL_FLOAT,
    GL_FALSE,
    0,
    None
)

glEnableVertexAttribArray(0)

vertex_source = """
#version 330 core

layout(location = 0) in vec3 aPos;

void main()
{
    gl_Position = vec4(aPos, 1.0);
}
"""

fragment_source = """#version 330 core

out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}"""

def create_shader(source, shader_type):
    shader = glCreateShader(shader_type)

    glShaderSource(shader, source)
    glCompileShader(shader)

    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader))

    return shader

vertex_shader = create_shader(
    vertex_source,
    GL_VERTEX_SHADER
)

fragment_shader = create_shader(
    fragment_source,
    GL_FRAGMENT_SHADER
)

program = glCreateProgram()

glAttachShader(program, vertex_shader)
glAttachShader(program, fragment_shader)

glLinkProgram(program)

glUseProgram(program)

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            raise SystemExit

    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(program)
    glBindVertexArray(vao)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    pygame.display.flip()