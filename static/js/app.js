const anwNameList = document.querySelector(".anw_name");
const abwDancersForm = document.querySelector("#abw-dancers-form");
const toBackendNotAnwInput = document.querySelector("#to-backend-not-anw");

//
const markUnmarkAnwName = e => {
    if (e.target.dataset.active == "active") {
        e.target.dataset.active = "inactive";
        e.target.style.background = "#fafafa";
    } else if (e.target.dataset.active == "inactive") {
        e.target.dataset.active = "active";
        e.target.style.background = "green";
    }
}


const submitAnwList = () => {
    let res = "";
    const allNotAnwDancers = [ ... document.querySelectorAll(".anw-name")].filter(an => an.dataset.active !== "active");

    [...allNotAnwDancers].forEach(na => {
        res += (na.dataset.dancerid + ",");
    });

    console.log(res)
    toBackendNotAnwInput.value = res;
}

// abwDancersForm.addEventListener("submit", submitAnwList);