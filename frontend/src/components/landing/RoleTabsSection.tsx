import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { LANDING_CONFIG } from '../../data/landing-data';

interface RoleCardProps {
  role: typeof LANDING_CONFIG.userRoles[0];
  isActive: boolean;
  onPress: () => void;
}

export const RoleCard: React.FC<RoleCardProps> = ({ role, isActive, onPress }) => {
  return (
    <TouchableOpacity
      style={[styles.roleCard, isActive && styles.roleCardActive]}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <View style={[styles.iconContainer, { backgroundColor: isActive ? role.color + '20' : '#F3F4F6' }]}>
        <Text style={[styles.roleIcon, { color: role.color }]}>{role.icon}</Text>
      </View>
      <Text style={[styles.roleTitle, isActive && { color: role.color }]}>{role.title}</Text>
    </TouchableOpacity>
  );
};

interface RoleFeatureListProps {
  role: typeof LANDING_CONFIG.userRoles[0];
}

const RoleFeatureList: React.FC<RoleFeatureListProps> = ({ role }) => {
  return (
    <View style={styles.featureList}>
      <Text style={styles.featureListTitle}>Key Benefits for {role.title}</Text>
      <View style={styles.featuresGrid}>
        {role.features.map((feature, index) => (
          <View key={index} style={styles.featureItem}>
            <Text style={[styles.featureCheck, { color: role.color }]}>✓</Text>
            <Text style={styles.featureText}>{feature}</Text>
          </View>
        ))}
      </View>
    </View>
  );
};

interface RoleTabsSectionProps {
  onSelectPlan: (planId: string) => void;
}

export const RoleTabsSection: React.FC<RoleTabsSectionProps> = ({ onSelectPlan }) => {
  const [activeRole, setActiveRole] = React.useState(LANDING_CONFIG.userRoles[0]);
  const activeRoleData = LANDING_CONFIG.userRoles.find(r => r.id === activeRole.id) || LANDING_CONFIG.userRoles[0];

  return (
    <View style={styles.container} id="roles">
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Built for Everyone in the School Ecosystem</Text>
        <Text style={styles.sectionSubtitle}>
          Whether you're an administrator, teacher, student, or parent, SchoolOps has tools tailored for your needs
        </Text>
      </View>
      
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.tabsContainer}
      >
        {LANDING_CONFIG.userRoles.map((role) => (
          <RoleCard
            key={role.id}
            role={role}
            isActive={activeRole.id === role.id}
            onPress={() => setActiveRole(role)}
          />
        ))}
      </ScrollView>
      
      <View style={styles.contentContainer}>
        <View style={styles.contentLeft}>
          <Text style={styles.roleDescriptionTitle}>{activeRoleData.title}</Text>
          <Text style={styles.roleDescription}>{activeRoleData.description}</Text>
          <RoleFeatureList role={activeRoleData} />
        </View>
        
        <View style={[styles.contentRight, { borderColor: activeRoleData.color }]}>
          <View style={styles.mockupHeader}>
            <View style={styles.mockupDots}>
              <View style={[styles.dot, { backgroundColor: '#EF4444' }]} />
              <View style={[styles.dot, { backgroundColor: '#F59E0B' }]} />
              <View style={[styles.dot, { backgroundColor: '#10B981' }]} />
            </View>
          </View>
          <View style={styles.mockupContent}>
            <View style={styles.mockupTitle}>
              <Text style={[styles.mockupTitleText, { color: activeRoleData.color }]}>{activeRoleData.title} Dashboard</Text>
            </View>
            <View style={styles.mockupStats}>
              <View style={[styles.mockupStat, { borderLeftColor: activeRoleData.color }]}>
                <Text style={styles.mockupStatValue}>94%</Text>
                <Text style={styles.mockupStatLabel}>Attendance</Text>
              </View>
              <View style={[styles.mockupStat, { borderLeftColor: activeRoleData.color }]}>
                <Text style={styles.mockupStatValue}>A-</Text>
                <Text style={styles.mockupStatLabel}>Performance</Text>
              </View>
            </View>
            <View style={styles.mockupList}>
              {[1, 2, 3].map((item) => (
                <View key={item} style={styles.mockupListItem}>
                  <View style={[styles.mockupListIcon, { backgroundColor: activeRoleData.color + '20' }]}>
                    <Text style={[styles.mockupListIconText, { color: activeRoleData.color }]}>✓</Text>
                  </View>
                  <View style={styles.mockupListLine} />
                </View>
              ))}
            </View>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 60,
    paddingHorizontal: 20,
    backgroundColor: '#F8FAFC',
  },
  sectionHeader: {
    alignItems: 'center',
    marginBottom: 40,
  },
  sectionTitle: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
    textAlign: 'center',
  },
  sectionSubtitle: {
    fontSize: 18,
    color: '#6B7280',
    textAlign: 'center',
    maxWidth: 600,
  },
  tabsContainer: {
    paddingHorizontal: 20,
    marginBottom: 40,
    justifyContent: 'center',
  },
  roleCard: {
    alignItems: 'center',
    padding: 20,
    marginHorizontal: 8,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    minWidth: 140,
  },
  roleCardActive: {
    borderColor: '#4F46E5',
    backgroundColor: '#FFFFFF',
  },
  iconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  roleIcon: {
    fontSize: 28,
  },
  roleTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
  },
  contentContainer: {
    flexDirection: 'row',
    maxWidth: 1100,
    alignSelf: 'center',
    width: '100%',
    gap: 40,
    alignItems: 'center',
  },
  contentLeft: {
    flex: 1,
  },
  roleDescriptionTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
  },
  roleDescription: {
    fontSize: 18,
    color: '#6B7280',
    marginBottom: 24,
  },
  featureList: {},
  featureListTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 16,
  },
  featuresGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '48%',
    marginBottom: 8,
  },
  featureCheck: {
    fontSize: 16,
    marginRight: 8,
  },
  featureText: {
    fontSize: 14,
    color: '#4B5563',
    flex: 1,
  },
  contentRight: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 3,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 10,
  },
  mockupHeader: {
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  mockupDots: {
    flexDirection: 'row',
    gap: 6,
  },
  dot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  mockupContent: {
    padding: 20,
  },
  mockupTitle: {
    marginBottom: 20,
  },
  mockupTitleText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  mockupStats: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 20,
  },
  mockupStat: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
  },
  mockupStatValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  mockupStatLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  mockupList: {
    gap: 12,
  },
  mockupListItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  mockupListIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  mockupListIconText: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  mockupListLine: {
    flex: 1,
    height: 8,
    backgroundColor: '#F3F4F6',
    borderRadius: 4,
  },
});
