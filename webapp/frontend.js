const slideTransitionTime = 500;
let slideTransitionAllowed = true;
const minTimeBetweenSlides = 0;

const serverURL = "http://127.0.0.1:8000/";

const pathname = window.location.pathname;
const rootDirectory = pathname.substring(0, pathname.lastIndexOf("/"));

const directory = "/home/tmuller/2023_03_Aegypten_HochzeitNayer/SHOW/Aegypten2023_FHD/files/";
function setSlides() {
    var slideShow = document.getElementById("slideshow");
    
	fetch(serverURL + "list_images/?" + new URLSearchParams({directory: directory}), {method: "GET", mode: "cors"})
		.then(response => response.json())
		.then(data => {
			console.log(data.images.length)
		    data.images.forEach(image => {
                var slide = document.createElement("div");
                slide.setAttribute("class", "slide fade");
                // slide.setAttribute("style", "backgroundImage:url(" + image + ")");
                slide.style.backgroundImage = "url(" + image + ")";
                slideShow.appendChild(slide);
		    });
	  	})
	  	.catch(error => {
			console.error(error);
		});
}
setSlides();

const title = document.title;
const slides = document.getElementsByClassName("slide");
const nSlides = document.getElementsByClassName("slide").length;
console.log(nSlides);

for (let slideIndex = 0; slideIndex < nSlides; slideIndex++) {
	slides[slideIndex].style.backgroundImage = slides[slideIndex].style.backgroundImage.replace("${rootDirectory}", rootDirectory);
	slides[slideIndex].style.transition = "opacity " + slideTransitionTime + "ms ease-in-out";
}

let currentSlideIndex = 0;
let nextSlideIndex = 0;
const urlParams = new URLSearchParams(window.location.search);
const slideParameter = parseInt(urlParams.get("slide"), 10);
if (!isNaN(slideParameter) && slideParameter >= 0) {
	nextSlideIndex = slideParameter - 1;
}

function showSlides() {
	nextSlideIndex = (nextSlideIndex + nSlides) % nSlides;
	slides[nextSlideIndex].style.display = "block";

	// Update URL with the current slideIndex
	const searchParams = new URLSearchParams();
	searchParams.set("slide", nextSlideIndex+1);
	const newURL = `${window.location.pathname}?${searchParams.toString()}`;
	window.history.pushState({path: newURL}, "", newURL);
	document.title = `Ägypten 2023 (${nextSlideIndex + 1}/${nSlides})`;

	for (let slideIndex = 0; slideIndex < nSlides; slideIndex++) {
		slides[slideIndex].style.display = (((slideIndex == currentSlideIndex) || (slideIndex == nextSlideIndex)) ? "block" : "none");
	}

	setTimeout(() => {
		slides[nextSlideIndex].style.opacity = 1;
		if (nextSlideIndex < currentSlideIndex) {
			slides[currentSlideIndex].style.opacity = 0;
		}
	}, 0); // Delay to ensure display and opacity changes happen together

	const tmpCurrentSlideIndex = currentSlideIndex;
	currentSlideIndex = nextSlideIndex;
	setTimeout(() => {
		if (tmpCurrentSlideIndex != nextSlideIndex) {
			slides[tmpCurrentSlideIndex].style.display = "none";
			slides[tmpCurrentSlideIndex].style.opacity = 0;
		}

	}, slideTransitionTime);
}

function nextSlide(steps=1) {
	if (!slideTransitionAllowed) {
		return;
	}

	slideTransitionAllowed = false;
	nextSlideIndex += steps;
	showSlides();

	setTimeout(() => {
		slideTransitionAllowed = true;
	}, slideTransitionTime + minTimeBetweenSlides);
}

document.addEventListener("keydown", function(event) {
	if (["ArrowRight", "Enter", " "].includes(event.key)) {
		nextSlide();
	} else if (["ArrowLeft", "Backspace"].includes(event.key)) {
		nextSlide(-1);
	} else if (["1"].includes(event.key)) {
		nextSlide(10);
	} else if (["2"].includes(event.key)) {
		nextSlide(20);
	} else if (["3"].includes(event.key)) {
		nextSlide(30);
	} else if (["4"].includes(event.key)) {
		nextSlide(40);
	} else if (["5"].includes(event.key)) {
		nextSlide(50);
	} else if (["6"].includes(event.key)) {
		nextSlide(60);
	} else if (["7"].includes(event.key)) {
		nextSlide(70);
	} else if (["8"].includes(event.key)) {
		nextSlide(80);
	} else if (["9"].includes(event.key)) {
		nextSlide(90);
	} else if (["0"].includes(event.key)) {
		nextSlide(100);
	} else if (["q"].includes(event.key)) {
		nextSlide(-10);
	} else if (["w"].includes(event.key)) {
		nextSlide(-20);
	} else if (["e"].includes(event.key)) {
		nextSlide(-30);
	} else if (["r"].includes(event.key)) {
		nextSlide(-40);
	} else if (["t"].includes(event.key)) {
		nextSlide(-50);
	} else if (["z", "y"].includes(event.key)) {
		nextSlide(-60);
	} else if (["u"].includes(event.key)) {
		nextSlide(-70);
	} else if (["i"].includes(event.key)) {
		nextSlide(-80);
	} else if (["o"].includes(event.key)) {
		nextSlide(-90);
	} else if (["p"].includes(event.key)) {
		nextSlide(-100);
	}
});

window.addEventListener("wheel", handleWheelEvent);
function handleWheelEvent(event) {
	if (event.deltaY > 0) {
		nextSlide();
	} else if (event.deltaY < 0) {
		nextSlide(-1);
	}
}

let touchStartX;
function handleTouchStart(event) {
	touchStartX = event.touches[0].clientX;
}
function handleTouchEnd(event) {
	const touchEndX = event.changedTouches[0].clientX;
	const deltaX = touchEndX - touchStartX;

	if (deltaX < 0) {
		nextSlide();
	} else if (deltaX > 0) {
		nextSlide(-1);
	}
}

showSlides();