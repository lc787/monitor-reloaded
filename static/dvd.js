let x = 0,
  y = 0,
  dirX = 1,
  dirY = 1;
  x2 = 0,
  y2 = 0,
  dirX2 = 1,
  dirY2 = 1;
const speed = 1.5;
const speed2 = 1;


let dvd = document.getElementById("dvd");
let dvd2 = document.getElementById("dvd2");

let black = document.getElementById("black");
const dvdWidth = dvd.clientWidth;
const dvdHeight = dvd.clientHeight;
const dvdWidth2 = dvd2.clientWidth;
const dvdHeight2 = dvd2.clientHeight;

function animate() {
  const screenHeight = document.body.clientHeight;
  const screenWidth = document.body.clientWidth;

  if (y + dvdHeight >= screenHeight || y < 0) {
    dirY *= -1;
  }
  if (x + dvdWidth >= screenWidth || x < 0) {
    dirX *= -1;


  }
  if (y2 + dvdHeight2 >= screenHeight || y < 0) {
    dirY2 *= -1;
  }
  if (x2 + dvdWidth2 >= screenWidth || x < 0) {
    dirX2 *= -1;


  }
  x += dirX * speed;
  y += dirY * speed;
  x2 += dirX2 * speed2;
  y2 += dirY2 * speed2;
  dvd.style.left = x + "px";
  dvd.style.top = y + "px";
  dvd2.style.left = x2 + "px";
  dvd2.style.top = y2 + "px";
  window.requestAnimationFrame(animate);
}

window.requestAnimationFrame(animate);
