import { Box, Heading, Text, VStack, SimpleGrid, Card, CardBody, Badge, HStack, Collapse, Progress, Divider, List, ListItem, ListIcon } from '@chakra-ui/react'
import { useState } from 'react'
import { CheckCircle2, AlertCircle, TrendingUp, Clock } from 'lucide-react'
import FileUpload from '../components/FileUpload'
import SkillRadar from '../components/SkillRadar'

const Analysis = () => {
    const [results, setResults] = useState(null)

    const handleAnalysisComplete = (data) => {
        // Use comprehensive evaluation data
        const evaluation = data.match?.overall_evaluation || {}
        const criteria = data.match?.criteria_scores || {}

        setResults({
            // Overall
            totalScore: evaluation.total_score || 0,
            fitLevel: evaluation.fit_level || 'Low',
            summary: evaluation.summary || 'No evaluation available',
            recommendation: data.match?.hiring_recommendation || 'N/A',

            // Detailed criteria
            criteria: criteria,

            // Key insights
            strengths: data.match?.key_strengths || [],
            concerns: data.match?.key_concerns || [],

            // Charts
            radarData: data.match?.radar_chart_data || [],

            // Legacy compatibility
            score: evaluation.total_score || 0,
            reasoning: evaluation.summary || data.match?.reasoning || 'No reasoning provided'
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

                        {/* Radar Chart */}
                        <Card>
                            <CardBody>
                                <Heading size="sm" mb={6}>10-Criteria Evaluation Breakdown</Heading>
                                <Box h="400px" w="full">
                                    <SkillRadar data={results.radarData} />
                                </Box>
                            </CardBody>
                        </Card>

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
                                                    <Box mt={2} p={2} bg="blue.50" borderRadius="md">
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
                                                        <Box flex={1} p={2} bg="purple.50" borderRadius="md">
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
