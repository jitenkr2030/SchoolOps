import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { LANDING_CONFIG, formatPrice, calculateYearlyDiscount } from '../../data/landing-data';

interface PricingCardProps {
  plan: typeof LANDING_CONFIG.pricing[0];
  isYearly: boolean;
  onSelect: (planId: string) => void;
}

export const PricingCard: React.FC<PricingCardProps> = ({ plan, isYearly, onSelect }) => {
  const price = isYearly ? plan.yearlyPrice : plan.monthlyPrice;
  const savings = calculateYearlyDiscount(plan.monthlyPrice, plan.yearlyPrice);
  const displayPrice = formatPrice(price);

  return (
    <View style={[styles.card, plan.popular && styles.cardPopular]}>
      {plan.popular && (
        <View style={styles.popularBadge}>
          <Text style={styles.popularText}>Most Popular</Text>
        </View>
      )}
      
      <View style={styles.cardHeader}>
        <Text style={[styles.planName, { color: plan.color }]}>{plan.name}</Text>
        <Text style={styles.planDescription}>{plan.description}</Text>
      </View>
      
      <View style={styles.priceContainer}>
        <Text style={styles.price}>{displayPrice}</Text>
        <Text style={styles.pricePeriod}>
          /{isYearly ? 'year' : 'month'}
        </Text>
      </View>
      
      {isYearly && savings > 0 && (
        <View style={styles.savingsBadge}>
          <Text style={styles.savingsText}>Save {savings}%</Text>
        </View>
      )}
      
      <View style={styles.featuresList}>
        {plan.features.map((feature, index) => (
          <View key={index} style={styles.featureItem}>
            <Text style={styles.checkIcon}>✓</Text>
            <Text style={styles.featureText}>{feature}</Text>
          </View>
        ))}
      </View>
      
      <TouchableOpacity
        style={[styles.ctaButton, { backgroundColor: plan.color }]}
        onPress={() => onSelect(plan.id)}
      >
        <Text style={styles.ctaButtonText}>{plan.cta}</Text>
      </TouchableOpacity>
    </View>
  );
};

interface PricingSectionProps {
  isYearly: boolean;
  setIsYearly: (value: boolean) => void;
  onSelectPlan: (planId: string) => void;
}

export const PricingSection: React.FC<PricingSectionProps> = ({ 
  isYearly, 
  setIsYearly, 
  onSelectPlan 
}) => {
  return (
    <View style={styles.container} id="pricing">
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Simple, Transparent Pricing</Text>
        <Text style={styles.sectionSubtitle}>
          Choose the plan that fits your school. All plans include core features.
        </Text>
      </View>
      
      <View style={styles.toggleContainer}>
        <TouchableOpacity
          style={[styles.toggleButton, !isYearly && styles.toggleButtonActive]}
          onPress={() => setIsYearly(false)}
        >
          <Text style={[styles.toggleText, !isYearly && styles.toggleTextActive]}>
            Monthly
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.toggleButton, isYearly && styles.toggleButtonActive]}
          onPress={() => setIsYearly(true)}
        >
          <Text style={[styles.toggleText, isYearly && styles.toggleTextActive]}>
            Yearly
          </Text>
          <View style={styles.discountBadge}>
            <Text style={styles.discountText}>Save 17%</Text>
          </View>
        </TouchableOpacity>
      </View>
      
      <ScrollView 
        horizontal 
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.cardsContainer}
      >
        {LANDING_CONFIG.pricing.map((plan) => (
          <PricingCard
            key={plan.id}
            plan={plan}
            isYearly={isYearly}
            onSelect={onSelectPlan}
          />
        ))}
      </ScrollView>
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
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 40,
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    padding: 4,
    alignSelf: 'center',
  },
  toggleButton: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  toggleButtonActive: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  toggleText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6B7280',
  },
  toggleTextActive: {
    color: '#1F2937',
  },
  discountBadge: {
    backgroundColor: '#10B981',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
    marginTop: 4,
  },
  discountText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: 'bold',
  },
  cardsContainer: {
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  card: {
    width: 320,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
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
  cardPopular: {
    borderWidth: 2,
    borderColor: '#4F46E5',
    transform: [{ scale: 1.02 }],
  },
  popularBadge: {
    position: 'absolute',
    top: -12,
    left: '50%',
    transform: [{ translateX: -60 }],
    backgroundColor: '#4F46E5',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
  },
  popularText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  cardHeader: {
    marginBottom: 20,
  },
  planName: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  planDescription: {
    fontSize: 14,
    color: '#6B7280',
  },
  priceContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 8,
  },
  price: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  pricePeriod: {
    fontSize: 16,
    color: '#6B7280',
    marginLeft: 4,
  },
  savingsBadge: {
    backgroundColor: '#D1FAE5',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginBottom: 20,
  },
  savingsText: {
    color: '#10B981',
    fontSize: 12,
    fontWeight: 'bold',
  },
  featuresList: {
    marginBottom: 24,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  checkIcon: {
    color: '#10B981',
    fontSize: 16,
    fontWeight: 'bold',
    marginRight: 10,
  },
  featureText: {
    fontSize: 14,
    color: '#4B5563',
    flex: 1,
  },
  ctaButton: {
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: 'center',
  },
  ctaButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
