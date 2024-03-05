export const friendsManager = () => {
    const areThereFriends = document.getElementById('friendsList');
    const styleCheckbox = document.getElementById('styleCheckbox');

    // Initially hide the friends list
    areThereFriends.style.display = 'none';

    styleCheckbox.addEventListener('change', (event) => {
        if (event.target.checked) {
            areThereFriends.style.display = 'block';
        } else {
            areThereFriends.style.display = 'none';
        }
    });
};
