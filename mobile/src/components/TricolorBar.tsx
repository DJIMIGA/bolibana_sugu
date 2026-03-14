import React from 'react';
import { View, StyleSheet } from 'react-native';

interface TricolorBarProps {
  width?: number;
  height?: number;
}

const TricolorBar: React.FC<TricolorBarProps> = ({ width = 120, height = 3 }) => (
  <View style={[styles.container, { width }]}>
    <View style={[styles.bar, { height, backgroundColor: '#009A00' }]} />
    <View style={[styles.bar, { height, backgroundColor: '#FFD700' }]} />
    <View style={[styles.bar, { height, backgroundColor: '#C0392B' }]} />
  </View>
);

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    gap: 4,
    alignSelf: 'center',
  },
  bar: {
    flex: 1,
    borderRadius: 2,
  },
});

export default TricolorBar;
