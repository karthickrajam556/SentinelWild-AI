const questionBox = document.getElementsByClassName("question__box");

for (let i = 0; i < questionBox.length; i++) {
  questionBox[i].addEventListener("click", function () {
    this.classList.toggle("active");
  });
}
