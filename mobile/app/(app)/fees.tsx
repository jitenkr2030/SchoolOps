import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  FlatList,
  TouchableOpacity,
} from 'react-native';
import {
  Text,
  Card,
  Button,
  Avatar,
  IconButton,
  Badge,
  Surface,
  Modal,
  TextInput,
} from 'react-native-paper';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../store/store';
import { setFees, addPayment } from '../../store/slices/feesSlice';
import { FEE_DATA } from '../../services/mockData';
import { formatDate, formatCurrency, getStatusColor } from '../../utils/helpers';
import { COLORS } from '../../theme';
import { useEffect } from 'react';

export default function FeesScreen() {
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useSelector((state: RootState) => state.auth);
  const { fees, totalDue, totalPaid } = useSelector((state: RootState) => state.fees);
  const [activeTab, setActiveTab] = useState<'pending' | 'paid' | 'all'>('pending');
  const [paymentModalVisible, setPaymentModalVisible] = useState(false);
  const [selectedFee, setSelectedFee] = useState<typeof FEE_DATA[0] | null>(null);
  const [paymentAmount, setPaymentAmount] = useState('');

  useEffect(() => {
    // Load mock fee data
    dispatch(setFees(FEE_DATA));
  }, [dispatch]);

  const filteredFees = fees.filter((fee) => {
    if (activeTab === 'pending') return fee.status !== 'Paid';
    if (activeTab === 'paid') return fee.status === 'Paid';
    return true;
  });

  const pendingFees = fees.filter((f) => f.status !== 'Paid');
  const paidFees = fees.filter((f) => f.status === 'Paid');

  const handlePayPress = (fee: typeof FEE_DATA[0]) => {
    setSelectedFee(fee);
    setPaymentAmount(fee.amount.toString());
    setPaymentModalVisible(true);
  };

  const handlePaymentConfirm = () => {
    if (selectedFee && paymentAmount) {
      dispatch(
        addPayment({
          feeId: selectedFee.id,
          amount: parseFloat(paymentAmount),
        })
      );
      setPaymentModalVisible(false);
      setSelectedFee(null);
      setPaymentAmount('');
    }
  };

  const renderFeeItem = ({ item }: { item: typeof fees[0] }) => (
    <Card style={styles.feeCard} mode="elevated">
      <Card.Content>
        <View style={styles.feeHeader}>
          <View style={styles.feeIconContainer}>
            <Text style={styles.feeIconText}>{item.feeType.charAt(0)}</Text>
          </View>
          <View style={styles.feeInfo}>
            <Text style={styles.feeType}>{item.feeType}</Text>
            <Text style={styles.feeAcademic}>{item.academicYear}</Text>
          </View>
          <Badge
            style={{
              backgroundColor: getStatusColor(item.status) + '20',
            }}
            textStyle={{
              color: getStatusColor(item.status),
              fontWeight: 'bold',
            }}
          >
            {item.status}
          </Badge>
        </View>

        <View style={styles.feeDetails}>
          <View style={styles.feeDetailItem}>
            <Text style={styles.feeDetailLabel}>Amount</Text>
            <Text style={styles.feeAmount}>{formatCurrency(item.amount)}</Text>
          </View>
          <View style={styles.feeDetailItem}>
            <Text style={styles.feeDetailLabel}>Due Date</Text>
            <Text style={styles.feeDetailValue}>{formatDate(item.dueDate)}</Text>
          </View>
        </View>

        {item.status === 'Paid' && (
          <View style={styles.paidBadge}>
            <Text style={styles.paidText}>Fully Paid</Text>
          </View>
        )}

        {item.status !== 'Paid' && (
          <View style={styles.paymentSection}>
            {item.paidAmount && item.paidAmount > 0 && (
              <View style={styles.partialPayment}>
                <Text style={styles.partialPaymentText}>
                  Already Paid: {formatCurrency(item.paidAmount)}
                </Text>
                <Text style={styles.remainingText}>
                  Remaining: {formatCurrency(item.amount - item.paidAmount)}
                </Text>
              </View>
            )}
            <Button
              mode="contained"
              onPress={() => handlePayPress(item)}
              style={styles.payButton}
              buttonColor={COLORS.primary}
            >
              Pay Now
            </Button>
          </View>
        )}
      </Card.Content>
    </Card>
  );

  return (
    <View style={styles.container}>
      {/* Summary Cards */}
      <View style={styles.summaryContainer}>
        <Card style={[styles.summaryCard, styles.summaryCardMain]} mode="elevated">
          <Card.Content>
            <Text style={styles.summaryTitle}>Total Outstanding</Text>
            <Text style={styles.summaryAmount}>
              {formatCurrency(totalDue)}
            </Text>
            <Text style={styles.summarySubtitle}>
              {pendingFees.length} pending fee{pendingFees.length !== 1 ? 's' : ''}
            </Text>
          </Card.Content>
        </Card>

        <View style={styles.summaryRow}>
          <Card style={styles.summaryCardSmall} mode="elevated">
            <Card.Content>
              <Text style={styles.summaryLabelSmall}>Paid This Year</Text>
              <Text style={[styles.summaryValueSmall, { color: COLORS.secondary }]}>
                {formatCurrency(totalPaid)}
              </Text>
            </Card.Content>
          </Card>
          <Card style={styles.summaryCardSmall} mode="elevated">
            <Card.Content>
              <Text style={styles.summaryLabelSmall}>Total Fees</Text>
              <Text style={styles.summaryValueSmall}>
                {formatCurrency(fees.reduce((sum, f) => sum + f.amount, 0))}
              </Text>
            </Card.Content>
          </Card>
        </View>
      </View>

      {/* Tabs */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'pending' && styles.activeTab]}
          onPress={() => setActiveTab('pending')}
        >
          <Text
            style={[
              styles.tabText,
              activeTab === 'pending' && styles.activeTabText,
            ]}
          >
            Pending ({pendingFees.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'paid' && styles.activeTab]}
          onPress={() => setActiveTab('paid')}
        >
          <Text
            style={[
              styles.tabText,
              activeTab === 'paid' && styles.activeTabText,
            ]}
          >
            Paid ({paidFees.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'all' && styles.activeTab]}
          onPress={() => setActiveTab('all')}
        >
          <Text
            style={[
              styles.tabText,
              activeTab === 'all' && styles.activeTabText,
            ]}
          >
            All
          </Text>
        </TouchableOpacity>
      </View>

      {/* Fee List */}
      <FlatList
        data={filteredFees}
        renderItem={renderFeeItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      />

      {/* Payment Modal */}
      <Modal
        visible={paymentModalVisible}
        onDismiss={() => setPaymentModalVisible(false)}
        contentContainerStyle={styles.modalContent}
      >
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Make Payment</Text>
          <IconButton
            icon="close"
            onPress={() => setPaymentModalVisible(false)}
          />
        </View>

        {selectedFee && (
          <View style={styles.modalBody}>
            <View style={styles.modalFeeInfo}>
              <Text style={styles.modalFeeType}>{selectedFee.feeType}</Text>
              <Text style={styles.modalFeeTotal}>
                Total: {formatCurrency(selectedFee.amount)}
              </Text>
            </View>

            <Text style={styles.inputLabel}>Payment Amount</Text>
            <TextInput
              mode="outlined"
              value={paymentAmount}
              onChangeText={setPaymentAmount}
              keyboardType="numeric"
              style={styles.input}
              left={<TextInput.Affix text="₹" />}
            />

            <View style={styles.quickAmounts}>
              {[25, 50, 75, 100].map((percent) => (
                <TouchableOpacity
                  key={percent}
                  style={styles.quickAmountButton}
                  onPress={() =>
                    setPaymentAmount(
                      Math.round((selectedFee.amount * percent) / 100).toString()
                    )
                  }
                >
                  <Text style={styles.quickAmountText}>{percent}%</Text>
                </TouchableOpacity>
              ))}
            </View>

            <Button
              mode="contained"
              onPress={handlePaymentConfirm}
              style={styles.confirmButton}
              buttonColor={COLORS.primary}
              disabled={!paymentAmount || parseFloat(paymentAmount) <= 0}
            >
              Confirm Payment
            </Button>

            <Text style={styles.modalNote}>
              This is a demo. No actual payment will be processed.
            </Text>
          </View>
        )}
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  summaryContainer: {
    padding: 16,
  },
  summaryCard: {
    borderRadius: 12,
    marginBottom: 12,
  },
  summaryCardMain: {
    backgroundColor: COLORS.primary,
  },
  summaryRow: {
    flexDirection: 'row',
    gap: 12,
  },
  summaryCardSmall: {
    flex: 1,
    borderRadius: 12,
  },
  summaryTitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  summaryAmount: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginVertical: 8,
  },
  summarySubtitle: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.8)',
  },
  summaryLabelSmall: {
    fontSize: 12,
    color: '#6B7280',
  },
  summaryValueSmall: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 4,
  },
  tabContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingBottom: 12,
    gap: 8,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
  },
  activeTab: {
    backgroundColor: COLORS.primary,
  },
  tabText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6B7280',
  },
  activeTabText: {
    color: '#FFFFFF',
  },
  listContent: {
    paddingHorizontal: 16,
    paddingBottom: 20,
  },
  feeCard: {
    borderRadius: 12,
    marginBottom: 12,
  },
  feeHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  feeIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: COLORS.primary + '20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  feeIconText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  feeInfo: {
    flex: 1,
  },
  feeType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  feeAcademic: {
    fontSize: 12,
    color: '#6B7280',
  },
  feeDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  feeDetailItem: {},
  feeDetailLabel: {
    fontSize: 12,
    color: '#6B7280',
  },
  feeAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  feeDetailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  paymentSection: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  partialPayment: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  partialPaymentText: {
    fontSize: 13,
    color: '#6B7280',
  },
  remainingText: {
    fontSize: 13,
    fontWeight: '600',
    color: COLORS.warning,
  },
  payButton: {
    borderRadius: 8,
  },
  paidBadge: {
    backgroundColor: COLORS.secondary + '20',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginTop: 12,
  },
  paidText: {
    color: COLORS.secondary,
    fontSize: 12,
    fontWeight: '600',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    margin: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  modalBody: {},
  modalFeeInfo: {
    marginBottom: 20,
  },
  modalFeeType: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  modalFeeTotal: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  input: {
    marginBottom: 16,
  },
  quickAmounts: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
    gap: 8,
  },
  quickAmountButton: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
  },
  quickAmountText: {
    fontSize: 13,
    fontWeight: '600',
    color: COLORS.primary,
  },
  confirmButton: {
    borderRadius: 8,
    marginBottom: 12,
  },
  modalNote: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
  },
});
