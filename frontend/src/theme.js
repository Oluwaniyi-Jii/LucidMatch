import { extendTheme } from '@chakra-ui/react'

const theme = extendTheme({
    config: {
        initialColorMode: 'light',
        useSystemColorMode: false,
    },
    colors: {
        brand: {
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
    },
    components: {
        Button: {
            baseStyle: {
                fontWeight: '600',
                borderRadius: 'lg',
            },
            variants: {
                solid: {
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
                },
            },
        },
        Card: {
            baseStyle: {
                container: {
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
