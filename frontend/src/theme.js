import { extendTheme } from '@chakra-ui/react'

const theme = extendTheme({
    config: {
        initialColorMode: 'light',
        useSystemColorMode: false,
    },
    colors: {
        brand: {
            50: '#F0FDFA',
            100: '#CCFBF1',
            200: '#99F6E4',
            300: '#5EEAD4',
            400: '#2DD4BF',
            500: '#14B8A6', // Primary Teal
            600: '#0D9488',
            700: '#0F766E',
            800: '#115E59',
            900: '#134E4A',
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
