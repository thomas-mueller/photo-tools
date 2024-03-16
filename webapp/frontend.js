class SlideShow {
	constructor(slideTransitionTime = 500, minTimeBetweenSlides = 0) {
		this.slideTransitionTime = slideTransitionTime;
		this.minTimeBetweenSlides = minTimeBetweenSlides;
	
		this.title = document.title;
		
		this.slides = document.getElementsByClassName("slide");
		for (let slideIndex = 0; slideIndex < this.slides.length; slideIndex++) {
			this.slides[slideIndex].style.transition = "opacity " + this.slideTransitionTime + "ms ease-in-out";
		}
		this.currentSlideIndex = 0;
		this.nextSlideIndex = 0;
		this.slideTransitionAllowed = true

		const urlParams = new URLSearchParams(window.location.search);
		const slideParameter = parseInt(urlParams.get("slide"), 10);
		if ((! isNaN(slideParameter)) && (slideParameter >= 0)) {
			this.nextSlideIndex = slideParameter - 1;
		}
		
		this.imageLabel = document.getElementById("image-label");
		this.filenameLabel = document.getElementById("filename-label");
		
		this.touchStartX;
		this.setControls();
	}
	
	showSlides() {
		this.nextSlideIndex = (this.nextSlideIndex + this.slides.length) % this.slides.length;
		this.slides[this.nextSlideIndex].style.display = "block";

		const searchParams = new URLSearchParams();
		searchParams.set("slide", this.nextSlideIndex+1);
		const newURL = window.location.pathname + "?" + searchParams.toString();
		window.history.pushState({path: newURL}, "", newURL);
		document.title = this.title + "(" + (this.nextSlideIndex + 1) + "/" + this.slides.length + ")";
		this.imageLabel.innerHTML = "Image " + (this.nextSlideIndex + 1) + "/" + this.slides.length;
		this.filenameLabel.innerHTML = this.slides[this.nextSlideIndex].style.backgroundImage.slice(4, -2).split("/").pop();

		for (let slideIndex = 0; slideIndex < this.slides.length; slideIndex++) {
			this.slides[slideIndex].style.display = (((slideIndex == this.currentSlideIndex) || (slideIndex == this.nextSlideIndex)) ? "block" : "none");
		}

		setTimeout(() => {
			this.slides[this.nextSlideIndex].style.opacity = 1;
			if (this.nextSlideIndex < this.currentSlideIndex) {
				this.slides[this.currentSlideIndex].style.opacity = 0;
			}
		}, 0);

		const tmpCurrentSlideIndex = this.currentSlideIndex;
		this.currentSlideIndex = this.nextSlideIndex;
		setTimeout(() => {
			if (tmpCurrentSlideIndex != this.nextSlideIndex) {
				this.slides[tmpCurrentSlideIndex].style.display = "none";
				this.slides[tmpCurrentSlideIndex].style.opacity = 0;
			}

		}, this.slideTransitionTime);
	}
	
	nextSlide(steps = 1) {
		if (! this.slideTransitionAllowed) {
			return;
		}

		this.slideTransitionAllowed = false;
		this.nextSlideIndex += steps;
		this.showSlides();

		setTimeout(() => {
			this.slideTransitionAllowed = true;
		}, this.slideTransitionTime + this.minTimeBetweenSlides);
	}

	handleTouchStart(event) {
		this.touchStartX = event.touches[0].clientX;
	}
	handleTouchEnd(event) {
		const touchEndX = event.changedTouches[0].clientX;
		const deltaX = touchEndX - this.touchStartX;
		this.nextSlide(event.deltaX < 0 ? 1 : -1);
	}
	
	keydownListener(event) {
		if (["ArrowRight", "Enter", " "].includes(event.key)) {
			this.nextSlide();
		} else if (["ArrowLeft", "Backspace"].includes(event.key)) {
			this.nextSlide(-1);
		} else if (["1"].includes(event.key)) {
			this.nextSlide(10);
		} else if (["2"].includes(event.key)) {
			this.nextSlide(20);
		} else if (["3"].includes(event.key)) {
			this.nextSlide(30);
		} else if (["4"].includes(event.key)) {
			this.nextSlide(40);
		} else if (["5"].includes(event.key)) {
			this.nextSlide(50);
		} else if (["6"].includes(event.key)) {
			this.nextSlide(60);
		} else if (["7"].includes(event.key)) {
			this.nextSlide(70);
		} else if (["8"].includes(event.key)) {
			this.nextSlide(80);
		} else if (["9"].includes(event.key)) {
			this.nextSlide(90);
		} else if (["0"].includes(event.key)) {
			this.nextSlide(100);
		} else if (["q"].includes(event.key)) {
			this.nextSlide(-10);
		} else if (["w"].includes(event.key)) {
			this.nextSlide(-20);
		} else if (["e"].includes(event.key)) {
			this.nextSlide(-30);
		} else if (["r"].includes(event.key)) {
			this.nextSlide(-40);
		} else if (["t"].includes(event.key)) {
			this.nextSlide(-50);
		} else if (["z", "y"].includes(event.key)) {
			this.nextSlide(-60);
		} else if (["u"].includes(event.key)) {
			this.nextSlide(-70);
		} else if (["i"].includes(event.key)) {
			this.nextSlide(-80);
		} else if (["o"].includes(event.key)) {
			this.nextSlide(-90);
		} else if (["p"].includes(event.key)) {
			this.nextSlide(-100);
		}
	}
	
	setControls() {
		document.addEventListener("keydown", event => {
			this.keydownListener(event)
		});

		window.addEventListener("wheel", event => {
			this.nextSlide(event.deltaY > 0 ? 1 : -1);
		});
	}
}

class ImageSorter extends SlideShow {
	constructor(slideTransitionTime = 0, minTimeBetweenSlides = 0) {
		super(slideTransitionTime=slideTransitionTime, minTimeBetweenSlides=minTimeBetweenSlides);
		
		this.images = Array.from(this.slides).map(slide => {
			return slide.style.backgroundImage.match(/url\("(.+)"\)/)[1];
		});
		
		this.currentSortedImageIndex = 0;
		this.nextSortedImageIndex = 0;
		this.sortedImages = [];
	}
	
	getConfiguration() {
		console.log(this.sortedImages);
	}
	
	setConfiguration(configuration) {
	}
	
	nextSortedImage(steps = 1) {
	}
	
	addCurrentImage(remove = false) {
		if (remove) {
			this.sortedImages.splice(this.currentSortedImageIndex, 1);
		} else {
			this.sortedImages.splice(this.currentSortedImageIndex, 0, this.images[this.currentSlideIndex]);
		}
		this.currentSortedImageIndex =+ (remove ? -1 : +1);
	}
	
	shiftCurrentSortedImage(steps = 1) {
	}
	
	toggleSelectCurrentImage() {
	}
	
	keydownListener(event) {
		if (["n"].includes(event.key)) {
			this.nextSortedImage();
		} else if (["p"].includes(event.key)) {
			this.nextSortedImage(steps=-1);
		} else if (["Enter"].includes(event.key)) {
			this.addCurrentImage();
		} else if (["Delete"].includes(event.key)) {
			this.addCurrentImage(remove=true);
		} else if (["+"].includes(event.key)) {
			this.shiftCurrentSortedImage();
		} else if (["-"].includes(event.key)) {
			this.shiftCurrentSortedImage(steps=-1);
		} else if (["m"].includes(event.key)) {
			this.toggleSelectCurrentImage();
		} else if (["s"].includes(event.key)) {
			this.getConfiguration();
		} else {
			super.keydownListener(event);
		}
	}
}

function listImages(directory, serverURL) {
	return fetch(serverURL + "list_images/?" + new URLSearchParams({directory: directory}), {method: "GET", mode: "cors"})
		.then(response => response.json())
		.then(data => {
			return data.images;
		})
		.catch(error => {
			throw error;
		});
}

function setSlides(directory, serverURL) {
	var slideShow = document.getElementById("slideshow");

	return listImages(directory, serverURL)
		.then(images => {
			return images.forEach(image => {
				var slide = document.createElement("div");
				slide.setAttribute("class", "slide fade");
				slide.style.backgroundImage = "url(" + image + ")";
				slideShow.appendChild(slide);
			});
		})
		.catch(error => {
			throw error;
		});
}
