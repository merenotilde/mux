const pixelContainer = document.querySelector('.animated-pixels-background');

function createPixel() {
    const pixel = document.createElement('div');
    pixel.style.width = '15px';
    pixel.style.height = '15px';
    pixel.style.position = 'absolute';
   
    pixel.style.opacity = '0.8';
    pixel.style.top = `${Math.random() * 100}vh`; 
    pixel.style.left = `${Math.random() * 100}vw`; 
    pixel.style.animation = `float 5s linear infinite alternate`;
    pixel.style.animationDelay = `${Math.random() * 5}s`; 

    pixelContainer.appendChild(pixel);
}
for (let i = 0; i < 10; i++) {
    createPixel();
}
