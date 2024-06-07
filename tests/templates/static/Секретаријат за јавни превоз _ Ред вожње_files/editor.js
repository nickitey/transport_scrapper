let paragraf = document.querySelectorAll(".editor p");
let containers = document.querySelectorAll(".editor div");

let paragraf_count = paragraf.length;
for (let i = 0; i < paragraf_count; i++){
    let link = paragraf[i];
    let slika = paragraf[i].firstChild.firstChild;

    if(link.firstChild.nodeName == 'A' && slika.nodeName == "IMG"){
        console.log(true);
        paragraf[i].classList.add("editor-link");
    }
  
}

let containers_count = containers.length;
for (let i = 0; i < containers_count; i++){
    let link = containers[i];
    let slika = containers[i].firstChild.firstChild;

    if(link.firstChild.nodeName == 'A' && slika.nodeName == "IMG"){
        console.log(true);
        containers[i].classList.add("editor-link");
    }
  
}
console.log(containers_count);

/* modul editor */
let paragraf_modul = document.querySelectorAll(".editor-modul p");
let containers_modul = document.querySelectorAll(".editor-modul div");

let paragraf_modul_count = paragraf_modul.length;
for (let i = 0; i < paragraf_modul_count; i++){
    let link = paragraf_modul[i];
    let slika = paragraf_modul[i].firstChild.firstChild;

    if(link.firstChild.nodeName == 'A' && slika.nodeName == "IMG"){
        console.log(true);
        paragraf_modul[i].classList.add("editor-link");
    }
  
}

let containers_modul_count = containers_modul.length;
for (let i = 0; i < containers_modul_count; i++){
    let link = containers_modul[i];
    let slika = containers_modul[i].firstChild.firstChild;

    if(link.firstChild.nodeName == 'A' && slika.nodeName == "IMG"){
        console.log(true);
        containers_modul[i].classList.add("editor-link");
    }
  
}
console.log(containers_count);