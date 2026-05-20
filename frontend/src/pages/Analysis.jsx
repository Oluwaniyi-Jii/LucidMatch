import { Box, Heading, Text, VStack, SimpleGrid, Card, CardBody, Badge, HStack, Collapse, Progress, Divider, List, ListItem, Button, IconButton, Tooltip } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import { CheckCircle2, AlertCircle, Clock, Trash2, ChevronDown, ChevronUp, History } from 'lucide-react'
import FileUpload from '../components/FileUpload'

const HISTORY_KEY = 'prism_analysis_history'

const Analysis = () => {
    const [results, setResults] = useState(null)
    const [history, setHistory] = useState([])
    const [expandedId, setExpandedId] = useState(null)

    // Load history from localStorage on mount
    useEffect(() => {
        try {
            const saved = localStorage.getItem(HISTORY_KEY)
            if (saved) setHistory(JSON.parse(saved))
        } catch {
            setHistory([])
        }
    }, [])

    const saveToHistory = (entry) => {
        const updated = [entry, ...history].slice(0, 20) // keep last 20
        setHistory(updated)
        localStorage.setItem(HISTORY_KEY, JSON.stringify(updated))
    }

    const deleteFromHistory = (id) => {
        const updated = history.filter(h => h.id !== id)
        setHistory(updated)
        localStorage.setItem(HISTORY_KEY, JSON.stringify(updated))
    }

    const clearHistory = () => {
        setHistory([])
        localStorage.removeItem(HISTORY_KEY)
    }

    const handleAnalysisComplete = (data) => {
        const evaluation = data.match?.overall_evaluation || {}
        const criteria = data.match?.criteria_scores || {}

        const newResult = {
            totalScore: evaluation.total_score || 0,
            fitLevel: evaluation.fit_level || 'Low',
            summary: evaluation.summary || 'No evaluation available',
            recommendation: data.match?.hiring_recommendation || 'N/A',
            criteria: criteria,
            strengths: data.match?.key_strengths || [],
            concerns: data.match?.key_concerns || [],
            score: evaluation.total_score || 0,
            reasoning: evaluation.summary || data.match?.reasoning || 'No reasoning provided'
        }

        setResults(newResult)

        // Save to history
        saveToHistory({
            id: Date.now(),
            timestamp: new Date().toLocaleString(),
            score: newResult.totalScore,
            fitLevel: newResult.fitLevel,
            recommendation: newResult.recommendation,
            summary: newResult.summary,
            strengths: newResult.strengths,
            concerns: newResult.concerns,
            criteria: newResult.criteria,
        })
    }

    const getScoreColor = (score) => {
        if (score >= 8) return 'green'
        if (score >= 5) return 'yellow'
        return 'red'
    }

    const getLevelColor = (level) => {
        if (level === 'High') return 'green'
        if (level === 'Medium') return 'yellow'
        return 'red'
    }

    return (
        <VStack spacing={8} align="stretch">

            {/* HISTORY PANEL - Always at the top */}
            {history.length > 0 && (
                <Card borderWidth="1px" borderColor="slate.200">
                    <CardBody>
                        <HStack justify="space-between" mb={4}>
                            <HStack>
                                <History size={18} color="gray" />
                                <Heading size="sm">Analysis History</Heading>
                                <Badge colorScheme="blue" borderRadius="full">{history.length}</Badge>
                            </HStack>
                            <Button size="xs" variant="ghost" colorScheme="red" leftIcon={<Trash2 size={12} />} onClick={clearHistory}>
                                Clear All
                            </Button>
                        </HStack>

                        <VStack spacing={3} align="stretch">
                            {history.map((item) => (
                                <Box key={item.id} border="1px solid" borderColor="slate.200" borderRadius="md" overflow="hidden">
                                    {/* Row header */}
                                    <HStack
                                        px={4} py={3}
                                        bg={expandedId === item.id ? 'brand.50' : 'slate.50'}
                                        justify="space-between"
                                        cursor="pointer"
                                        onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
                                        _hover={{ bg: 'brand.50' }}
                                    >
                                        <HStack spacing={4}>
                                            <Badge
                                                colorScheme={item.score >= 70 ? 'green' : item.score >= 50 ? 'yellow' : 'red'}
                                                fontSize="md"
                                                px={3} py={1}
                                                borderRadius="full"
                                            >
                                                {item.score}/100
                                            </Badge>
                                            <VStack align="start" spacing={0}>
                                                <Badge colorScheme={getLevelColor(item.fitLevel)} variant="subtle" fontSize="xs">
                                                    {item.fitLevel} Fit — {item.recommendation}
                                                </Badge>
                                                <Text fontSize="xs" color="slate.400">{item.timestamp}</Text>
                                            </VStack>
                                        </HStack>
                                        <HStack>
                                            <Tooltip label="Delete">
                                                <IconButton
                                                    icon={<Trash2 size={14} />}
                                                    size="xs"
                                                    variant="ghost"
                                                    colorScheme="red"
                                                    onClick={(e) => { e.stopPropagation(); deleteFromHistory(item.id) }}
                                                />
                                            </Tooltip>
                                            {expandedId === item.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                        </HStack>
                                    </HStack>

                                    {/* Expanded details */}
                                    {expandedId === item.id && (
                                        <Box px={4} py={3} bg="white">
                                            <Text fontSize="sm" color="slate.600" mb={3}>{item.summary}</Text>
                                            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} mb={3}>
                                                <Box>
                                                    <Text fontWeight="bold" fontSize="xs" color="green.600" mb={1}>STRENGTHS</Text>
                                                    {item.strengths?.slice(0, 3).map((s, i) => (
                                                        <Text key={i} fontSize="xs" color="slate.600">+ {s}</Text>
                                                    ))}
                                                </Box>
                                                <Box>
                                                    <Text fontWeight="bold" fontSize="xs" color="red.500" mb={1}>CONCERNS</Text>
                                                    {item.concerns?.slice(0, 3).map((c, i) => (
                                                        <Text key={i} fontSize="xs" color="slate.600">- {c}</Text>
                                                    ))}
                                                </Box>
                                            </SimpleGrid>
                                            {item.criteria && Object.keys(item.criteria).length > 0 && (
                                                <SimpleGrid columns={2} spacing={2}>
                                                    {Object.entries(item.criteria).slice(0, 4).map(([key, val]) => (
                                                        <HStack key={key} justify="space-between" p={2} bg="slate.50" borderRadius="md">
                                                            <Text fontSize="xs" textTransform="capitalize">{key.replace(/_/g, ' ')}</Text>
                                                            <Badge colorScheme={getScoreColor(val?.score || 0)} fontSize="xs">
                                                                {val?.score || 0}/10
                                                            </Badge>
                                                        </HStack>
                                                    ))}
                                                </SimpleGrid>
                                            )}
                                        </Box>
                                    )}
                                </Box>
                            ))}
                        </VStack>
                    </CardBody>
                </Card>
            )}

            <Box>
                <Heading size="lg" mb={2}>New Analysis</Heading>
                <Text color="slate.500">Upload a candidate resume to evaluate transferable skills.</Text>
            </Box>

            <FileUpload onAnalysisComplete={handleAnalysisComplete} />

            <Collapse in={!!results} animateOpacity>
                {results && (
                    <VStack spacing={6} align="stretch" mt={8}>
                        {/* Overall Evaluation Header */}
                        <Card bg="brand.50" borderWidth="2px" borderColor="brand.500">
                            <CardBody>
                                <VStack spacing={4} align="start">
                                    <HStack justify="space-between" w="full">
                                        <Box>
                                            <Text fontSize="sm" fontWeight="bold" color="slate.600" mb={1}>
                                                OVERALL FIT
                                            </Text>
                                            <Heading size="3xl" color="brand.600">
                                                {results.totalScore}/100
                                            </Heading>
                                        </Box>
                                        <VStack align="end">
                                            <Badge
                                                colorScheme={getLevelColor(results.fitLevel)}
                                                fontSize="lg"
                                                px={4}
                                                py={2}
                                                borderRadius="full"
                                            >
                                                {results.fitLevel} Fit
                                            </Badge>
                                            <Badge
                                                colorScheme={results.recommendation === 'Strong Hire' || results.recommendation === 'Hire' ? 'green' : 'gray'}
                                                fontSize="md"
                                                px={3}
                                                py={1}
                                            >
                                                {results.recommendation}
                                            </Badge>
                                        </VStack>
                                    </HStack>
                                    <Text color="slate.700" lineHeight="tall">
                                        {results.summary}
                                    </Text>
                                </VStack>
                            </CardBody>
                        </Card>

                        {/* Key Insights */}
                        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                            <Card>
                                <CardBody>
                                    <HStack mb={3}>
                                        <CheckCircle2 size={20} color="green" />
                                        <Heading size="sm">Key Strengths</Heading>
                                    </HStack>
                                    <List spacing={2}>
                                        {results.strengths.map((strength, i) => (
                                            <ListItem key={i} fontSize="sm" color="slate.600">
                                                - {strength}
                                            </ListItem>
                                        ))}
                                    </List>
                                </CardBody>
                            </Card>

                            <Card>
                                <CardBody>
                                    <HStack mb={3}>
                                        <AlertCircle size={20} color="orange" />
                                        <Heading size="sm">Key Concerns</Heading>
                                    </HStack>
                                    <List spacing={2}>
                                        {results.concerns.map((concern, i) => (
                                            <ListItem key={i} fontSize="sm" color="slate.600">
                                                - {concern}
                                            </ListItem>
                                        ))}
                                    </List>
                                </CardBody>
                            </Card>
                        </SimpleGrid>

                        {/* Detailed Criteria Scores */}
                        <Card>
                            <CardBody>
                                <Heading size="sm" mb={4}>Detailed Evaluation Criteria</Heading>
                                <VStack spacing={4} align="stretch">
                                    {Object.entries(results.criteria).map(([key, criterion]) => {
                                        const score = criterion.score || criterion.potential_score || 0
                                        const level = criterion.level || criterion.potential_level || 'Low'

                                        return (
                                            <Box key={key}>
                                                <HStack justify="space-between" mb={2}>
                                                    <Text fontWeight="bold" fontSize="sm" textTransform="capitalize">
                                                        {key.replace(/_/g, ' ')}
                                                    </Text>
                                                    <HStack>
                                                        <Badge colorScheme={getLevelColor(level)}>
                                                            {level}
                                                        </Badge>
                                                        <Text fontWeight="bold" color={`${getScoreColor(score)}.600`}>
                                                            {score}/10
                                                        </Text>
                                                    </HStack>
                                                </HStack>
                                                <Progress
                                                    value={score * 10}
                                                    colorScheme={getScoreColor(score)}
                                                    size="sm"
                                                    borderRadius="full"
                                                    mb={2}
                                                />
                                                {criterion.evidence && (
                                                    <Text fontSize="xs" color="slate.500" fontStyle="italic">
                                                        {criterion.evidence}
                                                    </Text>
                                                )}
                                                {key === 'trainable_skills' && criterion.skills_identified?.length > 0 && (
                                                    <Box mt={2} p={2} bg="teal.50" borderRadius="md">
                                                        <Text fontSize="xs" fontWeight="bold" mb={1}>Trainable Skills:</Text>
                                                        <Text fontSize="xs">{criterion.skills_identified.join(', ')}</Text>
                                                        {criterion.estimated_learning_time && (
                                                            <HStack mt={1}>
                                                                <Clock size={12} />
                                                                <Text fontSize="xs">{criterion.estimated_learning_time}</Text>
                                                            </HStack>
                                                        )}
                                                    </Box>
                                                )}
                                                {key === 'potential_readiness' && (
                                                    <HStack mt={2} spacing={4}>
                                                        <Box flex={1} p={2} bg="amber.50" borderRadius="md">
                                                            <Text fontSize="xs" fontWeight="bold">Potential: {criterion.potential_score}/10</Text>
                                                        </Box>
                                                        <Box flex={1} p={2} bg="green.50" borderRadius="md">
                                                            <Text fontSize="xs" fontWeight="bold">Readiness: {criterion.readiness_score}/10</Text>
                                                        </Box>
                                                    </HStack>
                                                )}
                                                <Divider mt={3} />
                                            </Box>
                                        )
                                    })}
                                </VStack>
                            </CardBody>
                        </Card>
                    </VStack>
                )}
            </Collapse>
        </VStack>
    )
}

export default Analysis
