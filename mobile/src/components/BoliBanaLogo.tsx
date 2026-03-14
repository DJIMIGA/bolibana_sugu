import React from 'react';
import Svg, { Path, Circle, Rect, Text as SvgText, G, Line } from 'react-native-svg';

interface BoliBanaLogoProps {
  size?: number;
  variant?: 'full' | 'icon' | 'navbar';
}

// Icône 64×64 — fond blanc avec bordure (bolibana_icon_64_blanc.svg)
export const BoliBanaLogoIcon: React.FC<{ size?: number }> = ({ size = 64 }) => (
  <Svg viewBox="0 0 64 64" width={size} height={size}>
    <Rect width={64} height={64} rx={14} fill="white" stroke="#eeeeee" strokeWidth={1} />
    <Path
      d="M12 26 L16 46 Q16 50 20 50 L44 50 Q48 50 48 46 L52 26Z"
      fill="none"
      stroke="#008000"
      strokeWidth={2.5}
      strokeLinejoin="round"
    />
    <Circle cx={23} cy={38} r={5} fill="#009A00" />
    <Circle cx={32} cy={38} r={5} fill="#FFD700" stroke="#D4A017" strokeWidth={0.7} />
    <Circle cx={41} cy={38} r={5} fill="#C0392B" />
    <Path
      d="M20 26 Q20 14 32 14 Q44 14 44 26"
      fill="none"
      stroke="#008000"
      strokeWidth={2.5}
      strokeLinecap="round"
    />
    <Circle cx={52} cy={20} r={7} fill="#C0392B" />
    <SvgText
      x={52}
      y={24.5}
      fontSize={8.5}
      fontWeight="700"
      fill="white"
      fontFamily="Georgia, serif"
      textAnchor="middle"
    >
      3
    </SvgText>
  </Svg>
);

// Icône 64×64 — fond vert (bolibana_icon_64_vert.svg)
export const BoliBanaLogoIconGreen: React.FC<{ size?: number }> = ({ size = 64 }) => (
  <Svg viewBox="0 0 64 64" width={size} height={size}>
    <Rect width={64} height={64} rx={14} fill="#008000" />
    <Path
      d="M12 26 L16 46 Q16 50 20 50 L44 50 Q48 50 48 46 L52 26Z"
      fill="none"
      stroke="rgba(255,255,255,0.9)"
      strokeWidth={2.5}
      strokeLinejoin="round"
    />
    <Circle cx={23} cy={38} r={5} fill="rgba(255,255,255,0.85)" />
    <Circle cx={32} cy={38} r={5} fill="#FFD700" />
    <Circle cx={41} cy={38} r={5} fill="#ff6f6f" />
    <Path
      d="M20 26 Q20 14 32 14 Q44 14 44 26"
      fill="none"
      stroke="rgba(255,255,255,0.9)"
      strokeWidth={2.5}
      strokeLinecap="round"
    />
    <Circle cx={52} cy={20} r={7} fill="#ff6f6f" />
    <SvgText
      x={52}
      y={24.5}
      fontSize={8.5}
      fontWeight="700"
      fill="white"
      fontFamily="Georgia, serif"
      textAnchor="middle"
    >
      3
    </SvgText>
  </Svg>
);

// Logo navbar compact — icône + "BoliBana SUGU" (bolibana_logo_navbar.svg)
export const BoliBanaLogoNavbar: React.FC<{ width?: number; height?: number }> = ({
  width = 160,
  height = 32,
}) => (
  <Svg viewBox="0 0 180 36" width={width} height={height}>
    <Path
      d="M4 10 L7 24 Q7 27 10 27 L28 27 Q31 27 31 24 L34 10Z"
      fill="none"
      stroke="#008000"
      strokeWidth={1.8}
      strokeLinejoin="round"
    />
    <Circle cx={12} cy={19} r={3.5} fill="#009A00" />
    <Circle cx={19} cy={19} r={3.5} fill="#FFD700" stroke="#D4A017" strokeWidth={0.5} />
    <Circle cx={26} cy={19} r={3.5} fill="#C0392B" />
    <Path
      d="M10 10 Q10 4 19 4 Q28 4 28 10"
      fill="none"
      stroke="#008000"
      strokeWidth={1.8}
      strokeLinecap="round"
    />
    <Circle cx={34} cy={7} r={4} fill="#C0392B" />
    <SvgText
      x={34}
      y={10.5}
      fontSize={5.5}
      fontWeight="700"
      fill="white"
      fontFamily="sans-serif"
      textAnchor="middle"
    >
      3
    </SvgText>
    <SvgText
      x={44}
      y={17}
      fontSize={16}
      fontWeight="700"
      fill="#008000"
      fontFamily="Georgia, serif"
      letterSpacing={-0.5}
    >
      Boli
    </SvgText>
    <SvgText
      x={82}
      y={17}
      fontSize={16}
      fontWeight="700"
      fill="#C8890A"
      fontFamily="Georgia, serif"
      letterSpacing={-0.5}
    >
      Bana
    </SvgText>
    <SvgText
      x={44}
      y={28}
      fontSize={8}
      fill="#C0392B"
      fontFamily="sans-serif"
      letterSpacing={3.5}
      fontWeight="600"
    >
      SUGU
    </SvgText>
  </Svg>
);

// Logo complet — icône + grand texte + tagline (bolibana_logo_principal.svg)
export const BoliBanaLogoFull: React.FC<{ width?: number; height?: number }> = ({
  width = 260,
  height = 70,
}) => (
  <Svg viewBox="0 0 300 80" width={width} height={height}>
    <Path
      d="M12 26 L17 48 Q17 53 22 53 L50 53 Q55 53 55 48 L60 26Z"
      fill="none"
      stroke="#008000"
      strokeWidth={2.2}
      strokeLinejoin="round"
    />
    <Circle cx={25} cy={40} r={5.5} fill="#009A00" />
    <Circle cx={36} cy={40} r={5.5} fill="#FFD700" stroke="#D4A017" strokeWidth={0.8} />
    <Circle cx={47} cy={40} r={5.5} fill="#C0392B" />
    <Path
      d="M22 26 Q22 12 36 12 Q50 12 50 26"
      fill="none"
      stroke="#008000"
      strokeWidth={2.2}
      strokeLinecap="round"
    />
    <Circle cx={60} cy={20} r={7} fill="#C0392B" />
    <SvgText
      x={60}
      y={24.5}
      fontSize={8}
      fontWeight="700"
      fill="white"
      fontFamily="Georgia, serif"
      textAnchor="middle"
    >
      3
    </SvgText>
    <SvgText
      x={80}
      y={34}
      fontSize={28}
      fontWeight="700"
      fill="#008000"
      fontFamily="Georgia, serif"
      letterSpacing={-1}
    >
      Boli
    </SvgText>
    <SvgText
      x={148}
      y={34}
      fontSize={28}
      fontWeight="700"
      fill="#C8890A"
      fontFamily="Georgia, serif"
      letterSpacing={-1}
    >
      Bana
    </SvgText>
    <SvgText
      x={80}
      y={52}
      fontSize={13}
      fill="#C0392B"
      fontFamily="sans-serif"
      letterSpacing={6}
      fontWeight="600"
    >
      SUGU
    </SvgText>
    <Line x1={80} y1={58} x2={240} y2={58} stroke="rgba(192,57,43,0.2)" strokeWidth={0.6} />
    <SvgText
      x={80}
      y={69}
      fontSize={8.5}
      fill="#bbbbbb"
      fontFamily="sans-serif"
      letterSpacing={0.4}
    >
      Votre intermédiaire expert du marché
    </SvgText>
  </Svg>
);

const BoliBanaLogo: React.FC<BoliBanaLogoProps> = ({ size = 64, variant = 'icon' }) => {
  switch (variant) {
    case 'full':
      return <BoliBanaLogoFull width={size * 4} height={size} />;
    case 'navbar':
      return <BoliBanaLogoNavbar width={size * 6.4} height={size} />;
    case 'icon':
    default:
      return <BoliBanaLogoIcon size={size} />;
  }
};

export default BoliBanaLogo;
