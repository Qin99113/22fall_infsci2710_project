class WEBGL {
  constructor(set) {
    this.canvas = set.canvas;
    this.webGLCurtain = new Curtains({container: "canvas"});
    this.planeElement = set.planeElement;
    this.count = 0;
    this.isClicked = false;
    this.params = {
      vertexShader: document.getElementById("vs").textContent, // our vertex shader ID
      fragmentShader: document.getElementById("fs").textContent, // our framgent shader ID
      widthSegments: 40,
      heightSegments: 40, // we now have 40*40*6 = 9600 vertices !
      uniforms: {
        time: {
          name: "uTime", // uniform name that will be passed to our shaders
          type: "1f", // this means our uniform is a float
          value: 0
        },
        mousepos: {
          name: "uMouse",
          type: "2f",
          value: [0, 0]
        },
        resolution: {
          name: "uReso",
          type: "2f",
          value: [innerWidth, innerHeight]
        },
        progress: {
          name: "uProgress",
          type: "1f",
          value: 0
        }
      }
    };
    
    this.gsap = gsap.timeline()

    this.texts = document.querySelectorAll(".title__slide");

    this.nextImage = this.nextImage.bind(this);
  }

  initPlane() {
    // create our plane mesh
    this.plane = this.webGLCurtain.addPlane(this.planeElement, this.params);

    // Create textures
    this.currentTexture = this.plane.createTexture("currentTexture");
    this.nextTexture = this.plane.createTexture("nextTexture");

    this.currentTexture.setSource(this.plane.images[this.count]);
    this.nextTexture.setSource(this.plane.images[this.count + 1]);
    
    // use the onRender method of our plane fired at each requestAnimationFrame call

    if (this.plane) {
      this.plane.onReady(() => {
        this.update();
        this.initEvent();
      });
    }
  }

  update() {
    this.plane.onRender(() => {
      this.plane.uniforms.time.value += 0.01; // update our time uniform value

      this.plane.uniforms.resolution.value = [innerWidth, innerHeight];
    });
  }

  initEvent() {
    this.plane.htmlElement.addEventListener("click", this.nextImage);
  }

  nextImage() {
    if (this.isClicked) return;
    this.isClicked = true;
    this.count++;

    const currentIndex = this.count % this.plane.images.length;
    const nextIndex = (this.count + 1) % this.plane.images.length;

    gsap.to(this.plane.uniforms.progress, 1.5, {
      value: 1,
      ease: "sine.inOut",
      onComplete: () => {
        this.currentTexture.setSource(this.plane.images[currentIndex]);
        this.nextTexture.setSource(this.plane.images[nextIndex]);

        this.plane.uniforms.progress.value = 0;

        this.isClicked = false;
      }
    });

    this.revealText(currentIndex);
  }

  revealText(index) {
    const currentText = this.texts[index];
    const previousText = !currentText.previousElementSibling
      ? this.texts[2]
      : currentText.previousElementSibling;
    
    const currentTextChild = currentText.querySelectorAll('.text__item')
    const previousTextChild = previousText.querySelectorAll('.text__item')
    
    this.gsap
      .to(previousTextChild, {
        duration: .5,
        y: gsap.utils.wrap([100, -100]),
        ease: "sine.inOut"
      })
      .to(currentTextChild, {
        duration: .7,
        y: gsap.utils.wrap([0, 0]),
        ease: "sine.inOut"
      });
  }
}

const webgl = new WEBGL({
  canvas: document.getElementById("canvas"),
  planeElement: document.getElementsByClassName("plane")[0]
});

webgl.initPlane();