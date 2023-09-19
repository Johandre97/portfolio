var css = document.querySelector('h6');
var color1 = document.querySelector('.color1');
var color2 = document.querySelector('.color2');
var body = document.querySelector('body');
var randomButton = document.getElementById('randomButton');

function setGradient() {
  body.style.background = "linear-gradient(to right, " + color1.value + ", " + color2.value + ")";
  css.textContent = body.style.background + ";";
}

function generateRandomColor() {
  var randomColor1 = getRandomColor();
  var randomColor2 = getRandomColor();

  color1.value = randomColor1;
  color2.value = randomColor2;

  setGradient();
}

function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

color1.value = "#e1cbcc";
color2.value = "#bf78c4";

color1.addEventListener("input", setGradient);
color2.addEventListener("input", setGradient);
randomButton.addEventListener("click", generateRandomColor);

// Set initial background gradient
setGradient();
