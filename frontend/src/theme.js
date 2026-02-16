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
        heading: '"Montserrat", sans-serif',
        body: '"Montserrat", sans-serif',
    },
    radii: {
        none: '0',
        sm: '0',
        base: '0',
        md: '0',
        lg: '0',
        xl: '0',
        '2xl': '0',
        '3xl': '0',
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
                borderRadius: '0',
                borderWidth: '1px',
                borderColor: 'slate.900',
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
                    borderColor: 'slate.900',
                    color: 'slate.700',
                    _hover: {
                        bg: 'slate.50',
                        borderColor: 'slate.900',
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
                    borderRadius: '0',
                    borderWidth: '1px',
                    borderColor: 'slate.900',
                    boxShadow: 'none',
                    overflow: 'hidden',
                },
            },
        },
        Heading: {
            baseStyle: {
                color: 'slate.900',
                letterSpacing: '0',
            },
        },
        Text: {
            baseStyle: {
                color: 'slate.600',
            },
        },
        Input: {
            baseStyle: {
                field: {
                    borderRadius: '0',
                    borderColor: 'slate.900',
                    _focus: {
                        borderColor: 'brand.500',
                        boxShadow: 'none',
                    }
                }
            },
            defaultProps: {
                focusBorderColor: 'brand.500',
            }
        },
        Select: {
            baseStyle: {
                field: {
                    borderRadius: '0',
                    borderColor: 'slate.900',
                    _focus: {
                        borderColor: 'brand.500',
                        boxShadow: 'none',
                    }
                }
            }
        },
        Textarea: {
            baseStyle: {
                borderRadius: '0',
                borderColor: 'slate.900',
                _focus: {
                    borderColor: 'brand.500',
                    boxShadow: 'none',
                }
            }
        },
        Badge: {
            baseStyle: {
                borderRadius: '0',
                border: '1px solid',
                borderColor: 'slate.900',
                px: 2,
                py: 0.5,
            }
        },
        Tag: {
            baseStyle: {
                container: {
                    borderRadius: '0',
                    border: '1px solid',
                    borderColor: 'slate.900',
                }
            }
        },
        Modal: {
            baseStyle: {
                dialog: {
                    borderRadius: '0',
                    border: '1px solid',
                    borderColor: 'slate.900',
                    boxShadow: 'none',
                }
            }
        },
        Menu: {
            baseStyle: {
                list: {
                    borderRadius: '0',
                    border: '1px solid',
                    borderColor: 'slate.900',
                    boxShadow: 'none',
                },
                item: {
                    _focus: {
                        bg: 'slate.50',
                    }
                }
            }
        },
        Popover: {
            baseStyle: {
                content: {
                    borderRadius: '0',
                    border: '1px solid',
                    borderColor: 'slate.900',
                    boxShadow: 'none',
                }
            }
        },
        Tooltip: {
            baseStyle: {
                borderRadius: '0',
                border: '1px solid',
                borderColor: 'slate.900',
                bg: 'white',
                color: 'slate.900',
                boxShadow: 'none',
            }
        },
    },
})

export default theme
