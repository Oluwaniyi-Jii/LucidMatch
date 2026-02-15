import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts'
import { useTheme } from '@chakra-ui/react'

const SkillRadar = ({ data }) => {
    const theme = useTheme()

    // Convert theme colors to hex for Recharts
    const gridColor = theme.colors.slate[200]
    const textColor = theme.colors.slate[600]
    const radarColor = theme.colors.brand[500]
    const radarFill = theme.colors.brand[500]

    // Comparison colors
    const candidateAColor = theme.colors.teal[500]
    const candidateBColor = theme.colors.amber[500]

    // Detect if this is comparison data (has candidateA field) or single candidate data (has score field)
    const isComparison = data && data.length > 0 && 'candidateA' in data[0]

    return (
        <ResponsiveContainer width="100%" height="100%" minWidth={200} minHeight={300}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                <PolarGrid stroke={gridColor} />
                <PolarAngleAxis dataKey="subject" tick={{ fill: textColor, fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 10]} tick={false} axisLine={false} />

                {isComparison ? (
                    <>
                        <Radar
                            name="Candidate A"
                            dataKey="candidateA"
                            stroke={candidateAColor}
                            strokeWidth={3}
                            fill={candidateAColor}
                            fillOpacity={0.3}
                        />
                        <Radar
                            name="Candidate B"
                            dataKey="candidateB"
                            stroke={candidateBColor}
                            strokeWidth={3}
                            fill={candidateBColor}
                            fillOpacity={0.3}
                        />
                    </>
                ) : (
                    <Radar
                        name="Candidate"
                        dataKey="score"
                        stroke={radarColor}
                        strokeWidth={3}
                        fill={radarFill}
                        fillOpacity={0.3}
                    />
                )}

                <Legend />
            </RadarChart>
        </ResponsiveContainer>
    )
}

export default SkillRadar
