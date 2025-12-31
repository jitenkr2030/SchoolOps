import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { LANDING_CONFIG } from '../../data/landing-data';

interface FAQItemProps {
  item: typeof LANDING_CONFIG.faqs[0];
  isExpanded: boolean;
  onToggle: () => void;
}

const FAQItem: React.FC<FAQItemProps> = ({ item, isExpanded, onToggle }) => {
  return (
    <View style={styles.faqItem}>
      <TouchableOpacity 
        style={styles.faqQuestion} 
        onPress={onToggle}
        activeOpacity={0.7}
      >
        <Text style={styles.questionText}>{item.question}</Text>
        <Text style={styles.expandIcon}>{isExpanded ? '−' : '+'}</Text>
      </TouchableOpacity>
      
      {isExpanded && (
        <View style={styles.faqAnswer}>
          <Text style={styles.answerText}>{item.answer}</Text>
        </View>
      )}
    </View>
  );
};

interface FAQSectionProps {
  onSelectPlan: (planId: string) => void;
}

export const FAQSection: React.FC<FAQSectionProps> = ({ onSelectPlan }) => {
  const [expandedId, setExpandedId] = React.useState<number | null>(1);

  const toggleFAQ = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <View style={styles.container} id="faq">
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>Frequently Asked Questions</Text>
        <Text style={styles.sectionSubtitle}>
          Got questions? We've got answers. If you don't see your question here, feel free to contact us.
        </Text>
      </View>
      
      <View style={styles.faqList}>
        {LANDING_CONFIG.faqs.map((faq) => (
          <FAQItem
            key={faq.id}
            item={faq}
            isExpanded={expandedId === faq.id}
            onToggle={() => toggleFAQ(faq.id)}
          />
        ))}
      </View>
      
      <View style={styles.contactBox}>
        <Text style={styles.contactTitle}>Still have questions?</Text>
        <Text style={styles.contactText}>
          Our team is here to help. Contact us and we'll get back to you within 24 hours.
        </Text>
        <TouchableOpacity 
          style={styles.contactButton}
          onPress={() => onSelectPlan('contact')}
        >
          <Text style={styles.contactButtonText}>Contact Sales</Text>
        </TouchableOpacity>
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
  faqList: {
    maxWidth: 800,
    alignSelf: 'center',
    marginBottom: 40,
  },
  faqItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  faqQuestion: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  questionText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
    paddingRight: 16,
  },
  expandIcon: {
    fontSize: 24,
    color: '#4F46E5',
    fontWeight: 'bold',
  },
  faqAnswer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  answerText: {
    fontSize: 15,
    color: '#6B7280',
    lineHeight: 24,
    paddingTop: 16,
  },
  contactBox: {
    backgroundColor: '#4F46E5',
    borderRadius: 20,
    padding: 40,
    alignItems: 'center',
    maxWidth: 600,
    alignSelf: 'center',
  },
  contactTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginBottom: 12,
  },
  contactText: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
    textAlign: 'center',
    marginBottom: 24,
  },
  contactButton: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 10,
  },
  contactButtonText: {
    color: '#4F46E5',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
