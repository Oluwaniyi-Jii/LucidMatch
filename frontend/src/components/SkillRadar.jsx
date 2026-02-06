import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts'
import { useTheme } from '@chakra-ui/react'

const SkillRadar = ({ data }) => {
    const theme = useTheme()

    // Convert theme colors to hex for Recharts
    const gridColor = theme.colors.slate[200]
    const textColor = theme.colors.slate[600]
    const radarColor = theme.colors.brand[500]
    const radarFill = theme.colors.brand[500]

    return (
        <ResponsiveContainer width="100%" height="100%" minWidth={200} minHeight={300}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                <PolarGrid stroke={gridColor} />
                <PolarAngleAxis dataKey="subject" tick={{ fill: textColor, fontSize: 12 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                <Radar
                    name="Candidate"
                    dataKey="A"
                    stroke={radarColor}
                    strokeWidth={3}
                    fill={radarFill}
                    fillOpacity={0.3}
                />
                <Legend />
            </RadarChart>
        </ResponsiveContainer>
    )
}

export default SkillRadar
