export const authenticatedFetch = async (url, options = {}) => {
    const token = localStorage.getItem('auth_token');

    // Default headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });

        if (response.status === 401) {
            // Clear invalid token
            localStorage.removeItem('auth_token');
            // Redirect to login
            window.location.href = '/login';
            throw new Error("Unauthorized");
        }

        return response;
    } catch (error) {
        throw error;
    }
};
