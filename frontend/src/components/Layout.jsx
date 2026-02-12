import { Box, Flex, Icon, Text, VStack } from '@chakra-ui/react'
import { LayoutDashboard, FileText, ShieldCheck, BookOpen, Briefcase } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

const NavItem = ({ icon, children, to }) => {
    const location = useLocation()
    const isActive = location.pathname === to

    return (
        <Link to={to} style={{ width: '100%' }}>
            <Flex
                align="center"
                p="3"
                mx="4"
                borderRadius="lg"
                role="group"
                cursor="pointer"
                bg={isActive ? 'brand.50' : 'transparent'}
                color={isActive ? 'brand.600' : 'slate.600'}
                _hover={{
                    bg: isActive ? 'brand.50' : 'slate.50',
                    color: isActive ? 'brand.600' : 'slate.900',
                }}
                fontWeight={isActive ? '600' : '500'}
                transition="all 0.2s"
            >
                <Icon
                    mr="4"
                    fontSize="20"
                    as={icon}
                    color={isActive ? 'brand.600' : 'slate.400'}
                    _groupHover={{
                        color: isActive ? 'brand.600' : 'slate.600',
                    }}
                />
                {children}
            </Flex>
        </Link>
    )
}

const Layout = ({ children }) => {
    return (
        <Flex h="100vh" bg="slate.50">
            {/* Sidebar */}
            <Box
                w="64"
                bg="white"
                borderRight="1px"
                borderColor="slate.200"
                display={{ base: 'none', md: 'block' }}
                py="8"
            >
                <Flex align="center" px="8" mb="10">
                    <Text fontSize="2xl" fontWeight="bold" color="brand.600" letterSpacing="tight">
                        Prism
                    </Text>
                </Flex>

                <VStack spacing="1" align="stretch">
                    <NavItem icon={LayoutDashboard} to="/">Dashboard</NavItem>
                    <NavItem icon={Briefcase} to="/jobs">Job Board</NavItem>
                    <NavItem icon={FileText} to="/analysis">New Analysis</NavItem>
                    <NavItem icon={ShieldCheck} to="/governance">Governance</NavItem>
                    <NavItem icon={BookOpen} to="/upskill">Curriculum</NavItem>
                </VStack>
            </Box>

            {/* Main Content */}
            <Box flex="1" overflowY="auto" p="8">
                <Box maxW="7xl" mx="auto">
                    {children}
                </Box>
            </Box>
        </Flex>
    )
}

export default Layout
