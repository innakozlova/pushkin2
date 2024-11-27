// получаем доступ к элементу кнопки наверх
const goTopBtn=document.querySelector("#go-top");
// однократная прокрутка в пикселях
const scrollStep =-150;

//обработчик событий прокрутки окна
window.addEventListener("scroll", trackScroll);

//обработчик нажатия на кнопку
window.addEventListener("click", goTop);

function trackScroll() {
    // положение верхушки страницы
    const scrolled=window.scrollY; 
    // высота клиентской области окна
    const coords=document.documentElement.clientHeight;
    // если прокрутили на один экран, то кнопка появится
    if (scrolled > coords)
        goTopBtn.classList.add("go-top--show");
    else
        goTopBtn.classList.remove("go-top--show");
}

// функция прокрутки наверх при нажатии кнопку
function goTop() {
    // ЕСЛИ окно проркучено, то 
    if (window.scrollY > 0) {
        // в этом случае едем наверх
    window.scrollBy(0,scrollStep); // прокручиваем на переменную
    // рекурсивный вызов
    setTimeout(goTop, 0);
    }
} 
// console.log(goTopBtn);