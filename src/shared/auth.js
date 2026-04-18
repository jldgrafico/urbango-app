const auth = {
    saveSession(data) {
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
    },

    getToken() {
        return localStorage.getItem('token');
    },

    getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isLoggedIn() {
        return !!this.getToken();
    },

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/passenger/login.html';
    },

    requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = '/passenger/login.html';
            return false;
        }
        return true;
    }
};

export default auth;