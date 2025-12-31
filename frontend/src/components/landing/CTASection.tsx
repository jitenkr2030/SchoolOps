import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { LANDING_CONFIG } from '../../data/landing-data';

interface CTASectionProps {
  onSelectPlan: (planId: string) => void;
}

export const CTASection: React.FC<CTASectionProps> = ({ onSelectPlan }) => {
  const router = useRouter();

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>{LANDING_CONFIG.cta.title}</Text>
        <Text style={styles.subtitle}>{LANDING_CONFIG.cta.subheadline}</Text>
        
        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.primaryButton}
            onPress={() => router.push('/register' as any)}
          >
            <Text style={styles.primaryButtonText}>{LANDING_CONFIG.cta.buttonText}</Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.secondaryButton}
            onPress={() => router.push('/demo' as any)}
          >
            <Text style={styles.secondaryButtonText}>Request Demo</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.trustBadges}>
          <View style={styles.badge}>
            <Text style={styles.badgeIcon}>🔒</Text>
            <Text style={styles.badgeText}>No credit card required</Text>
          </View>
          <View style={styles.badge}>
            <Text style={styles.badgeIcon}>✓</Text>
            <Text style={styles.badgeText}>14-day free trial</Text>
          </View>
          <View style={styles.badge}>
            <Text style={styles.badgeIcon}>💬</Text>
            <Text style={styles.badgeText}>24/7 support</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

interface FooterSectionProps {}

export const FooterSection: React.FC<FooterSectionProps> = () => {
  const router = useRouter();
  const { footer } = LANDING_CONFIG;

  return (
    <View style={styles.footer} id="contact">
      <View style={styles.footerContent}>
        <View style={styles.footerBrand}>
          <View style={styles.logo}>
            <Text style={styles.logoText}>S</Text>
          </View>
          <Text style={styles.brandName}>{footer.company.name}</Text>
          <Text style={styles.brandDescription}>{footer.company.description}</Text>
          
          <View style={styles.socialLinks}>
            {Object.entries(footer.company.social).map(([platform, link], index) => (
              <TouchableOpacity key={platform} style={styles.socialIcon}>
                <Text style={styles.socialText}>
                  {platform === 'twitter' ? '𝕏' : platform === 'linkedin' ? 'in' : 'f'}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        
        <View style={styles.footerLinks}>
          <View style={styles.linkColumn}>
            <Text style={styles.linkColumnTitle}>Product</Text>
            {footer.product.map((link, index) => (
              <TouchableOpacity 
                key={index} 
                style={styles.linkItem}
                onPress={() => router.push(link.href as any)}
              >
                <Text style={styles.linkText}>{link.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <View style={styles.linkColumn}>
            <Text style={styles.linkColumnTitle}>Company</Text>
            {footer.companyLinks.map((link, index) => (
              <TouchableOpacity 
                key={index} 
                style={styles.linkItem}
                onPress={() => router.push(link.href as any)}
              >
                <Text style={styles.linkText}>{link.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
          
          <View style={styles.linkColumn}>
            <Text style={styles.linkColumnTitle}>Legal</Text>
            {footer.legal.map((link, index) => (
              <TouchableOpacity 
                key={index} 
                style={styles.linkItem}
                onPress={() => router.push(link.href as any)}
              >
                <Text style={styles.linkText}>{link.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>
      
      <View style={styles.footerBottom}>
        <Text style={styles.copyright}>
          © 2024 {footer.company.name}. All rights reserved.
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#4F46E5',
    paddingVertical: 80,
    paddingHorizontal: 20,
  },
  content: {
    maxWidth: 800,
    alignItems: 'center',
    alignSelf: 'center',
  },
  title: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#FFFFFF',
    textAlign: 'center',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 20,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    marginBottom: 40,
    maxWidth: 600,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 40,
  },
  primaryButton: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
  },
  primaryButtonText: {
    color: '#4F46E5',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    paddingHorizontal: 32,
    paddingVertical: 16,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: 'rgba(255, 255, 255, 0.5)',
  },
  secondaryButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
  trustBadges: {
    flexDirection: 'row',
    gap: 32,
  },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  badgeIcon: {
    fontSize: 16,
    marginRight: 8,
  },
  badgeText: {
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: 14,
  },
  footer: {
    backgroundColor: '#1F2937',
    paddingVertical: 60,
    paddingHorizontal: 20,
  },
  footerContent: {
    maxWidth: 1200,
    flexDirection: 'row',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    alignSelf: 'center',
    width: '100%',
  },
  footerBrand: {
    width: 300,
    marginBottom: 40,
  },
  logo: {
    width: 48,
    height: 48,
    backgroundColor: '#4F46E5',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  logoText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
  brandName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 8,
  },
  brandDescription: {
    fontSize: 14,
    color: '#9CA3AF',
    lineHeight: 24,
    marginBottom: 20,
  },
  socialLinks: {
    flexDirection: 'row',
    gap: 12,
  },
  socialIcon: {
    width: 40,
    height: 40,
    backgroundColor: '#374151',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  socialText: {
    fontSize: 16,
    color: '#FFFFFF',
  },
  footerLinks: {
    flexDirection: 'row',
    gap: 60,
    flexWrap: 'wrap',
  },
  linkColumn: {
    marginBottom: 20,
  },
  linkColumnTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 16,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  linkItem: {
    marginBottom: 10,
  },
  linkText: {
    fontSize: 14,
    color: '#9CA3AF',
  },
  footerBottom: {
    borderTopWidth: 1,
    borderTopColor: '#374151',
    marginTop: 40,
    paddingTop: 20,
    alignItems: 'center',
  },
  copyright: {
    fontSize: 14,
    color: '#6B7280',
  },
});
