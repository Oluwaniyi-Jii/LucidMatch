/**
 * LucidMatch Custom Theme
 * Modern, professional design for HR/Enterprise software
 */

import { extendTheme } from '@chakra-ui/react';

const theme = extendTheme({
    config: {
        initialColorMode: 'light',
        useSystemColorMode: false,
    },
    colors: {
        brand: {
            50: '#e6f2ff',
            100: '#b3d9ff',
            200: '#80bfff',
            300: '#4da6ff',
            400: '#1a8cff',
            500: '#0073e6',
            600: '#005bb3',
            700: '#004280',
            800: '#002a4d',
            900: '#00111a',
        },
        success: {
            500: '#38A169',
        },
        warning: {
            500: '#DD6B20',
        },
        danger: {
            500: '#E53E3E',
        },
    },
    fonts: {
        heading: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
        body: `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
    },
    components: {
        Button: {
            baseStyle: {
                fontWeight: '600',
                borderRadius: 'lg',
            },
            variants: {
                solid: {
                    bg: 'brand.500',
                    color: 'white',
                    _hover: {
                        bg: 'brand.600',
                    },
                },
                outline: {
                    borderColor: 'brand.500',
                    color: 'brand.500',
                },
            },
        },
        Card: {
            baseStyle: {
                container: {
                    borderRadius: 'xl',
                    boxShadow: 'md',
                },
            },
        },
    },
    styles: {
        global: {
            body: {
                bg: 'gray.50',
            },
        },
    },
});

export default theme;
