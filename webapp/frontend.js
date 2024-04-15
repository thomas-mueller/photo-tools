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
		
		this.touchStartX;
		this.setControls();
	}
	
	toggleFullScreenMode() {
		var isFullScreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
		if (! isFullScreen) {
			const element = document.documentElement;
			if (element.requestFullscreen) {
				element.requestFullscreen();
			} else if (element.webkitRequestFullscreen) {
				element.webkitRequestFullscreen();
			} else if (element.msRequestFullscreen) {
				element.msRequestFullscreen();
			}
		} else {
			if (document.exitFullscreen) {
				document.exitFullscreen();
			} else if (document.webkitExitFullscreen) {
				document.webkitExitFullscreen();
			} else if (document.msExitFullscreen) {
				document.msExitFullscreen();
			}
		}
	}
	
	updateView() {
		this.nextSlideIndex = (this.nextSlideIndex + this.slides.length) % this.slides.length;
		this.slides[this.nextSlideIndex].style.display = "block";

		const searchParams = new URLSearchParams();
		searchParams.set("slide", this.nextSlideIndex+1);
		const newURL = window.location.pathname + "?" + searchParams.toString();
		window.history.pushState({path: newURL}, "", newURL);
		document.title = this.title + "(" + (this.nextSlideIndex + 1) + "/" + this.slides.length + ")";

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
	
	nextSlide(steps = 1, newIndex = null) {
		if (! this.slideTransitionAllowed) {
			return;
		}

		this.slideTransitionAllowed = false;
		if (newIndex === null) {
			this.nextSlideIndex += steps;
		} else {
			this.nextSlideIndex = newIndex;
		}
		this.updateView();

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
		if (["F11"].includes(event.key)) {
			this.toggleFullScreenMode();
		} else if (["ArrowRight", "Enter", " "].includes(event.key)) {
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
		
		this.currentSortedImageIndex = null;
		this.sortedImages = [];

		document.addEventListener("fullscreenchange", this.handleFullScreenChange);
		document.addEventListener("webkitfullscreenchange", this.handleFullScreenChange);
		document.addEventListener("mozfullscreenchange", this.handleFullScreenChange);
		document.addEventListener("msfullscreenchange", this.handleFullScreenChange);
	}

	handleFullScreenChange() {
		var fullScreenButton = document.getElementById("full-button");
		var isFullScreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
		if (isFullScreen) {
			fullScreenButton.className = "button-small";
		} else {
			fullScreenButton.className = "button-full";
		}
	}
	
	updateView() {
		super.updateView();

		this.imageLabel = document.getElementById("image-label");
		this.imageLabel.innerHTML = (this.nextSlideIndex + 1) + "/" + this.slides.length;
		// this.imageLabel.innerHTML = "Image " + (this.nextSlideIndex + 1) + "/" + this.slides.length;

		this.filenameLabel = document.getElementById("filename-label");
		this.filenameLabel.innerHTML = this.slides[this.nextSlideIndex].style.backgroundImage.slice(4, -2).split("/").pop();
		
		this.sortedImageLabel = document.getElementById("sorted-image-label");
		const sortedIndicesOfCurrentImage = this.sortedImages.reduce(
			(indices, element, index) => (element === this.images[this.currentSlideIndex]) ? indices.concat(index) : indices, []
		);
		if (sortedIndicesOfCurrentImage.length == 0) {
			this.currentSortedImageIndex = null;
			this.sortedImageLabel.innerHTML = "-/" + this.sortedImages.length;
		} else {
			this.currentSortedImageIndex = sortedIndicesOfCurrentImage[0];
			this.sortedImageLabel.innerHTML = sortedIndicesOfCurrentImage.map(index => index+1).join(",") + "/" + this.sortedImages.length;
		}
	}
	
	getConfiguration() {
		console.log(this.sortedImages);
	}
	
	setConfiguration(configuration) {
	}
	
	nextSortedImage(steps = 1, newIndex = null) {
		if (newIndex === null) {
			if (this.currentSortedImageIndex == null) {
				this.currentSortedImageIndex = 0;
				(steps >= 0 ? this.images.slice(this.currentSlideIndex) : this.images.slice(0, this.currentSlideIndex+1).reverse()).forEach(
					(image) => {
						const sortedImageIndex = this.sortedImages.indexOf(image);
						if (sortedImageIndex >= 0) {
							this.currentSortedImageIndex = sortedImageIndex - 1;
							return;
						}
					}
				);
			}
			this.currentSortedImageIndex += steps;
		} else {
			this.currentSortedImageIndex = newIndex;
		}
		this.currentSortedImageIndex = (this.currentSortedImageIndex + this.sortedImages.length) % this.sortedImages.length;
		
		const nextSlideIndex = this.images.indexOf(this.sortedImages[this.currentSortedImageIndex]);
		this.nextSlide(null, nextSlideIndex);
	}
	
	addCurrentImage(remove = false) {
		if (remove) {
			if (this.sortedImages[this.currentSortedImageIndex] == this.images[this.currentSlideIndex]) {
				this.sortedImages.splice(this.currentSortedImageIndex, 1);
			}
		} else {
			// this.sortedImages.splice(this.currentSortedImageIndex+1, 0, this.images[this.currentSlideIndex]);
			this.sortedImages.push(this.images[this.currentSlideIndex]);
			this.nextSortedImage(null, this.sortedImages.length - 1);
		}
		// this.currentSortedImageIndex += (remove ? -1 : +1);
		
		this.updateView();
	}
	
	shiftCurrentSortedImage(steps = 1, newIndex = null) {
		if (this.currentSortedImageIndex !== null) {
			if (newIndex === null) {
				newIndex = this.currentSortedImageIndex + steps;
			}
			newIndex = Math.max(0, Math.min(newIndex, this.sortedImages.length-1));

			const imageToShift = this.sortedImages.splice(this.currentSortedImageIndex, 1)[0];
			this.sortedImages.splice(newIndex, 0, imageToShift);
			this.currentSortedImageIndex = newIndex;
			
			this.updateView();
		}
	}
	
	toggleSelectCurrentImage() {
		var selectButton = document.getElementById("select-button");
		selectButton.className = (selectButton.className == "button-select" ? "button-unselect" : "button-select");
	}
	
	keydownListener(event) {
		if (["n"].includes(event.key)) {
			this.nextSortedImage();
		} else if (["p"].includes(event.key)) {
			this.nextSortedImage(-1);
		} else if (["Enter"].includes(event.key)) {
			this.addCurrentImage(false);
		} else if (["Delete"].includes(event.key)) {
			this.addCurrentImage(true);
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
