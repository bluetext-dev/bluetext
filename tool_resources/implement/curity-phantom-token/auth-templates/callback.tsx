import { useEffect } from 'react';
import { useNavigate } from 'react-router';
import { useAuth } from '@clients/clients/phantom-token-handler/AuthContext';

export default function Callback() {
    const { isPageLoaded, isLoggedIn } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (isPageLoaded) {
            navigate('/', { replace: true });
        }
    }, [isPageLoaded, navigate]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4" />
                <p className="text-muted-foreground">Completing sign in...</p>
            </div>
        </div>
    );
}
