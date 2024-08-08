function toggleDescription(link) {
    const shortDesc = link.previousElementSibling.previousElementSibling;
    const fullDesc = link.previousElementSibling;
    
    if (fullDesc.style.display === "none") {
        fullDesc.style.display = "inline";
        shortDesc.style.display = "none";
        link.textContent = "Read less";
    } else {
        fullDesc.style.display = "none";
        shortDesc.style.display = "inline";
        link.textContent = "Read more";
    }
}

