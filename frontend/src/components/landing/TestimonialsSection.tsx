import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { LANDING_CONFIG } from '../../data/landing-data';

interface TestimonialCardProps {
  testimonial: typeof LANDING_CONFIG.testimonials[0];
}

export const TestimonialCard: React.FC<TestimonialCardProps> = ({ testimonial }) => {
  return (
    <View style={[styles.card, { borderTopWidth: 4, borderTopColor: testimonial.color }]}>
      <View style={styles.ratingContainer}>
        {[1, 2, 3, 4, 5].map((star) => (
          <Text key={star} style={styles.starIcon}>★</Text>
        ))}
      </View>
      
      <Text style={styles.content}>{testimonial.content}</Text>
      
      <View style={styles.authorContainer}>
        <View style={[styles.avatar, { backgroundColor: testimonial.color + '20' }]}>
          <Text style={[styles.avatarText, { color: testimonial.color }]}>
            {testimonial.avatar}
          </Text>
        </View>
        <View style={styles.authorInfo}>
          <Text style={styles.authorName}>{testimonial.name}</Text>
          <Text style={styles.authorRole}>{testimonial.role}</Text>
          <Text style={styles.schoolName}>{testimonial.school}</Text>
        </View>
      </View>
    </View>
  );
};

interface TestimonialsSectionProps {
  onSelectPlan: (planId: string) => void;
}

export const TestimonialsSection: React.FC<TestimonialsSectionProps> = ({ onSelectPlan }) => {
  return (
    <View style={styles.container} id="testimonials">
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Trusted by Schools Worldwide</Text>
        <Text style={styles.sectionSubtitle}>
          See what educators, administrators, and parents are saying about SchoolOps
        </Text>
      </View>
      
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.cardsContainer}
      >
        {LANDING_CONFIG.testimonials.map((testimonial) => (
          <TestimonialCard key={testimonial.id} testimonial={testimonial} />
        ))}
      </ScrollView>
      
      <View style={styles.trustIndicators}>
        <Text style={styles.trustTitle}>Trusted by leading institutions</Text>
        <View style={styles.logoGrid}>
          {['Delhi Public School', 'Ryan International', 'DAV Public', 'Jain Heritage', 'Narayana Group'].map((school, index) => (
            <View key={index} style={styles.logoItem}>
              <Text style={styles.schoolLogo}>{school.charAt(0)}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingVertical: 60,
    paddingHorizontal: 20,
    backgroundColor: '#FFFFFF',
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
  cardsContainer: {
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  card: {
    width: 360,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 28,
    marginHorizontal: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 5,
  },
  ratingContainer: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  starIcon: {
    fontSize: 18,
    color: '#F59E0B',
    marginRight: 4,
  },
  content: {
    fontSize: 15,
    color: '#4B5563',
    lineHeight: 26,
    marginBottom: 24,
    fontStyle: 'italic',
  },
  authorContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 26,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 14,
  },
  avatarText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  authorInfo: {
    flex: 1,
  },
  authorName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  authorRole: {
    fontSize: 14,
    color: '#6B7280',
  },
  schoolName: {
    fontSize: 13,
    color: '#9CA3AF',
    marginTop: 2,
  },
  trustIndicators: {
    marginTop: 60,
    alignItems: 'center',
  },
  trustTitle: {
    fontSize: 14,
    color: '#9CA3AF',
    marginBottom: 24,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  logoGrid: {
    flexDirection: 'row',
    justifyContent: 'center',
    flexWrap: 'wrap',
    gap: 20,
  },
  logoItem: {
    width: 100,
    height: 50,
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  schoolLogo: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#9CA3AF',
  },
});
