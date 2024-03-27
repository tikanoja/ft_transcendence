export const settingsCreation = () => {
    const selectLanguage = (lang) => {
        document.getElementById("selectedLanguage").innerText = "Selected Language: " + lang;
        console.log("Selected Language: " + lang);
    };

    const sendLang = (button) => {
        const lang = button.dataset.lang;
        selectLanguage(lang);
    };

    const languageButtons = document.querySelectorAll(".langButton");
    languageButtons.forEach(button => {
        button.addEventListener("click", () => {
            sendLang(button);
        });
    });
};
