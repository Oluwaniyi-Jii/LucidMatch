import { Box, Flex, Icon, Text, HStack } from '@chakra-ui/react'
import { LayoutDashboard, FileText, ShieldCheck, BookOpen, Briefcase } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

const NavItem = ({ icon, children, to }) => {
    const location = useLocation()
    const isActive = location.pathname === to

    return (
        <Link to={to}>
            <Flex
                align="center"
                px="4"
                py="2"
                borderRadius="lg"
                cursor="pointer"
                bg={isActive ? 'brand.50' : 'transparent'}
                color={isActive ? 'brand.600' : 'slate.600'}
                _hover={{
                    bg: isActive ? 'brand.50' : 'slate.100',
                    color: isActive ? 'brand.600' : 'slate.900',
                }}
                fontWeight={isActive ? '600' : '500'}
                transition="all 0.2s"
            >
                <Icon
                    mr={2}
                    fontSize="18"
                    as={icon}
                    color={isActive ? 'brand.600' : 'slate.400'}
                />
                <Text fontSize="sm">{children}</Text>
            </Flex>
        </Link>
    )
}

const Layout = ({ children }) => {
    return (
        <Box minH="100vh" bg="slate.50">
            {/* Topbar */}
            <Box
                bg="white"
                borderBottom="1px"
                borderColor="slate.200"
                position="sticky"
                top="0"
                zIndex="10"
            >
                <Flex
                    maxW="7xl"
                    mx="auto"
                    px="8"
                    py="4"
                    align="center"
                    justify="space-between"
                >
                    <Link to="/">
                        <Text
                            fontSize="2xl"
                            fontWeight="bold"
                            color="brand.600"
                            letterSpacing="tight"
                            cursor="pointer"
                            textTransform="uppercase"
                            _hover={{ color: 'brand.700' }}
                            transition="color 0.2s"
                        >
                            Prism
                        </Text>
                    </Link>
                    <HStack spacing="2">
                        <NavItem icon={LayoutDashboard} to="/">Dashboard</NavItem>
                        <NavItem icon={Briefcase} to="/jobs">Job Board</NavItem>
                        <NavItem icon={FileText} to="/analysis">New Analysis</NavItem>
                        <NavItem icon={ShieldCheck} to="/governance">Governance</NavItem>
                        <NavItem icon={BookOpen} to="/upskill">Curriculum</NavItem>
                    </HStack>
                </Flex>
            </Box>

            {/* Main Content */}
            <Box p="8">
                <Box maxW="7xl" mx="auto">
                    {children}
                </Box>
            </Box>
        </Box>
    )
}

export default Layout
