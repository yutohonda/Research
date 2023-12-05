#version 400 core

in vec2 outTextureCoord;
out vec4 outFragmentColor;
uniform sampler2D texture0;

vec2 distort(vec2 uv, float rate){
    uv -= 0.5;
    uv /= 1 - length(uv) * rate;
    uv += 0.5;
    return uv;
}


float rand(vec2 co){
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43756.5453);
}

vec4 gaussianBlur(ivec2 texSize, vec4 col, sampler2D tex, vec2 uv){
    float Pi = 6.28318530718;
    float Directions = 16.0; // BLUR DIRECTIONS (Default 16.0 - More is better but slower)
    float Quality = 3.0; // BLUR QUALITY (Default 4.0 - More is better but slower)
    float Size = 2.0; // BLUR SIZE (Radius)

    vec2 Radius = Size/texSize.xy;
    
    for( float d=0.0; d<Pi; d+=Pi/Directions)
    {
		for(float i=1.0/Quality; i<=1.0; i+=1.0/Quality)
        {
			col += texture(tex, uv+vec2(cos(d),sin(d))*Radius*i);		
        }
    }
    
    col /= Quality * Directions - 15.0;
    return col;
}

float ease_in_out_cubic(float x)
{
    return x < 0.5
        ? 4 * x * x * x
        : 1 - pow(-2 * x + 2, 3) / 2; 
}

float ease_In_Out_Quad(float x)
{
    return x < 0.5 
        ? 2 * x * x 
        : 1 - pow(-2 * x + 2, 2) / 2;
}

float crt_ease(float x, float base, float offset)
{
    float tmp =  x + offset - 1 * floor(x + offset);
    float xx = 1 - abs(tmp * 2 - 1);
    float ease = ease_In_Out_Quad(xx);
    return ease * base + base * 0.8; // base:rgb
}

void main(void) {
    vec2 uv = distort(outTextureCoord, 0.1);
    if(uv.x < 0 || 1 < uv.x || uv.y < 0 || 1 < uv.y )
    {
        outFragmentColor = vec4(0, 0, 0, 1);
        return;
    }

    vec4 color = texture(texture0, uv);

    ivec2 textureSize = textureSize(texture0, 0);
    float floor_x = fract(outTextureCoord.x * textureSize.x / 3);
    
    float isR = (floor_x <= 0.3) ? 1 : 0;
    float isG = (0.3 < floor_x && floor_x <= 0.6) ? 1 : 0;
    float isB = (0.6 < floor_x) ? 1 : 0;

    vec2 dx = vec2(1 / textureSize.x, 0);
    vec2 dy = vec2(0, 1/textureSize.y);

    int offset = 10;
    uv += isR * offset * -dy;
    uv += isB * offset * dy;

    color = gaussianBlur(textureSize, color, texture0, uv);

    float yPixelLength = 10;
    float floor_y = fract(outTextureCoord.y * textureSize.y / yPixelLength);
    float rand = 0.1;
    float ease_r = crt_ease(floor_y, color.r, rand);
    float ease_g = crt_ease(floor_y, color.g, rand);
    float ease_b = crt_ease(floor_y, color.b, rand);

    outFragmentColor = vec4((isR + 0.8) * ease_r, (isG + 0.8) * ease_g, (isB + 0.8) * ease_b, color.a);
    
}