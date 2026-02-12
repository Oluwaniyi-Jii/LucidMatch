<<<<<<< HEAD
import { extendTheme } from '@chakra-ui/react'
=======
/**
 * LucidMatch Custom Theme
 * Modern, professional design for HR/Enterprise software
 */

import { extendTheme } from '@chakra-ui/react';
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965

const theme = extendTheme({
    config: {
        initialColorMode: 'light',
        useSystemColorMode: false,
    },
    colors: {
        brand: {
<<<<<<< HEAD
            50: '#F0F5FF',
            100: '#E0EAFF',
            200: '#C7D2FE',
            300: '#A5B4FC',
            400: '#818CF8',
            500: '#6366F1', // Primary Indigo
            600: '#4F46E5',
            700: '#4338CA',
            800: '#3730A3',
            900: '#312E81',
        },
        slate: {
            50: '#F8FAFC',
            100: '#F1F5F9',
            200: '#E2E8F0',
            300: '#CBD5E1',
            400: '#94A3B8',
            500: '#64748B',
            600: '#475569',
            700: '#334155',
            800: '#1E293B',
            900: '#0F172A',
        }
    },
    fonts: {
        heading: '"Outfit", sans-serif',
        body: '"Outfit", sans-serif',
    },
    styles: {
        global: {
            body: {
                bg: 'slate.50',
                color: 'slate.900',
            },
        },
=======
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
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
    },
    components: {
        Button: {
            baseStyle: {
                fontWeight: '600',
                borderRadius: 'lg',
            },
            variants: {
                solid: {
<<<<<<< HEAD
                    bg: 'brand.600',
                    color: 'white',
                    _hover: {
                        bg: 'brand.700',
                    },
                    _active: {
                        bg: 'brand.800',
                    },
                },
                outline: {
                    borderColor: 'slate.200',
                    color: 'slate.700',
                    _hover: {
                        bg: 'slate.50',
                        borderColor: 'slate.300',
                    },
                },
                ghost: {
                    color: 'slate.600',
                    _hover: {
                        bg: 'slate.50',
                        color: 'slate.900',
                    },
=======
                    bg: 'brand.500',
                    color: 'white',
                    _hover: {
                        bg: 'brand.600',
                    },
                },
                outline: {
                    borderColor: 'brand.500',
                    color: 'brand.500',
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
                },
            },
        },
        Card: {
            baseStyle: {
                container: {
<<<<<<< HEAD
                    bg: 'white',
                    borderRadius: 'xl',
                    borderWidth: '1px',
                    borderColor: 'slate.100',
                    boxShadow: 'sm', // Subtle shadow, minimal depth
                    overflow: 'hidden',
                },
            },
        },
        Heading: {
            baseStyle: {
                color: 'slate.900',
                letterSpacing: '-0.02em',
            },
        },
        Text: {
            baseStyle: {
                color: 'slate.600',
            },
        },
    },
})

export default theme
=======
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
>>>>>>> 04f2e20865491a82877a9095f96d8deea5f10965
