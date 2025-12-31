import React from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  RefreshControl,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import {
  Text,
  Card,
  Avatar,
  IconButton,
  Surface,
  ProgressBar,
} from 'react-native-paper';
import { useRouter } from 'expo-router';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store/store';
import { logoutUser } from '../../store/slices/authSlice';
import { DASHBOARD_STATS, QUICK_ACTIONS, ATTENDANCE_DATA, HOMEWORK_DATA, FEE_DATA } from '../../services/mockData';
import { formatDate, formatCurrency, getStatusColor } from '../../utils/helpers';
import { COLORS } from '../../theme';

const { width } = Dimensions.get('window');
const CARD_WIDTH = (width - 48) / 2;

export default function HomeScreen() {
  const router = useRouter();
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useSelector((state: RootState) => state.auth);
  const [refreshing, setRefreshing] = React.useState(false);

  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1500);
  }, []);

  if (!user) return null;

  const stats = DASHBOARD_STATS[user.role as keyof typeof DASHBOARD_STATS] || [];
  const actions = QUICK_ACTIONS[user.role as keyof typeof QUICK_ACTIONS] || [];

  const renderStatCard = (item: typeof stats[0], index: number) => (
    <Card key={index} style={styles.statCard} mode="elevated">
      <Card.Content style={styles.statContent}>
        <View style={[styles.statIcon, { backgroundColor: item.color + '20' }]}>
          <Text style={[styles.statIconText, { color: item.color }]}>{item.icon.charAt(0).toUpperCase()}</Text>
        </View>
        <View style={styles.statInfo}>
          <Text style={styles.statValue}>{item.value}</Text>
          <Text style={styles.statLabel}>{item.label}</Text>
        </View>
      </Card.Content>
    </Card>
  );

  const renderActionCard = (action: typeof actions[0], index: number) => (
    <TouchableOpacity
      key={index}
      style={styles.actionCard}
      onPress={() => router.push(`/(app)/${action.screen}` as any)}
    >
      <View style={styles.actionContent}>
        <View style={[styles.actionIcon, { backgroundColor: COLORS.primary + '15' }]}>
          <Text style={styles.actionIconText}>{action.icon.charAt(0).toUpperCase()}</Text>
        </View>
        <Text style={styles.actionLabel}>{action.label}</Text>
      </View>
      <IconButton icon="chevron-right" size={20} color="#9CA3AF" />
    </TouchableOpacity>
  );

  const renderAttendancePreview = () => (
    <Card style={styles.sectionCard} mode="elevated">
      <Card.Title
        title="Recent Attendance"
        left={(props) => <Avatar.Icon {...props} icon="calendar-check" style={{ backgroundColor: COLORS.primary + '20' }} />}
        right={(props) => (
          <TouchableOpacity onPress={() => router.push('/(app)/academics')}>
            <Text style={styles.viewAll}>View All</Text>
          </TouchableOpacity>
        )}
      />
      <Card.Content>
        <View style={styles.attendanceRow}>
          {ATTENDANCE_DATA.slice(0, 5).map((record, index) => (
            <View key={record.id} style={styles.attendanceDay}>
              <Text style={styles.dayName}>{record.day.substring(0, 3)}</Text>
              <View style={[styles.statusDot, { backgroundColor: record.color }]} />
              <Text style={styles.statusText}>{record.status}</Text>
            </View>
          ))}
        </View>
      </Card.Content>
    </Card>
  );

  const renderHomeworkPreview = () => (
    <Card style={styles.sectionCard} mode="elevated">
      <Card.Title
        title="Pending Homework"
        left={(props) => <Avatar.Icon {...props} icon="book-open-variant" style={{ backgroundColor: COLORS.secondary + '20' }} />}
        right={(props) => (
          <TouchableOpacity onPress={() => router.push('/(app)/academics')}>
            <Text style={styles.viewAll}>View All</Text>
          </TouchableOpacity>
        )}
      />
      <Card.Content>
        {HOMEWORK_DATA.filter(h => h.status === 'pending').slice(0, 3).map((homework) => (
          <View key={homework.id} style={styles.homeworkItem}>
            <View style={styles.homeworkInfo}>
              <Text style={styles.homeworkTitle}>{homework.title}</Text>
              <Text style={styles.homeworkSubject}>{homework.subject} • Due {formatDate(homework.dueDate)}</Text>
            </View>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor('Pending') + '20' }]}>
              <Text style={[styles.statusBadgeText, { color: getStatusColor('Pending') }]}>Pending</Text>
            </View>
          </View>
        ))}
      </Card.Content>
    </Card>
  );

  const renderFeesPreview = () => (
    <Card style={styles.sectionCard} mode="elevated">
      <Card.Title
        title="Fee Status"
        left={(props) => <Avatar.Icon {...props} icon="cash" style={{ backgroundColor: COLORS.error + '20' }} />}
        right={(props) => (
          <TouchableOpacity onPress={() => router.push('/(app)/fees')}>
            <Text style={styles.viewAll}>View All</Text>
          </TouchableOpacity>
        )}
      />
      <Card.Content>
        <View style={styles.feeSummary}>
          <View style={styles.feeItem}>
            <Text style={styles.feeLabel}>Total Due</Text>
            <Text style={[styles.feeAmount, { color: COLORS.error }]}>
              {formatCurrency(FEE_DATA.filter(f => f.status !== 'Paid').reduce((sum, f) => sum + f.amount, 0))}
            </Text>
          </View>
          <View style={styles.feeItem}>
            <Text style={styles.feeLabel}>Due Dates</Text>
            <Text style={styles.feeAmount}>
              {FEE_DATA.filter(f => f.status === 'Pending' || f.status === 'Overdue').length} pending
            </Text>
          </View>
        </View>
        <ProgressBar
          progress={0.65}
          color={COLORS.secondary}
          style={styles.progressBar}
        />
        <Text style={styles.progressText}>65% of fees paid this year</Text>
      </Card.Content>
    </Card>
  );

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[COLORS.primary]} />
      }
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerLeft}>
          <Text style={styles.greeting}>Hello,</Text>
          <Text style={styles.userName}>{user.firstName} {user.lastName}</Text>
          <View style={styles.roleBadge}>
            <Text style={styles.roleText}>{user.role.toUpperCase()}</Text>
          </View>
        </View>
        <TouchableOpacity onPress={() => router.push('/(app)/profile')}>
          <Avatar.Text
            size={48}
            label={user.firstName.charAt(0) + (user.lastName?.charAt(0) || '')}
            style={{ backgroundColor: COLORS.primary + '20' }}
            color={COLORS.primary}
          />
        </TouchableOpacity>
      </View>

      {/* Stats Grid */}
      <View style={styles.statsContainer}>
        {stats.map((item, index) => renderStatCard(item, index))}
      </View>

      {/* Quick Actions */}
      {actions.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionsGrid}>
            {actions.map((action, index) => (
              <TouchableOpacity
                key={index}
                style={styles.quickActionCard}
                onPress={() => router.push(`/(app)/${action.screen}` as any)}
              >
                <View style={[styles.quickActionIcon, { backgroundColor: COLORS.primary + '15' }]}>
                  <Text style={styles.quickActionIconText}>{action.icon.charAt(0).toUpperCase()}</Text>
                </View>
                <Text style={styles.quickActionLabel}>{action.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      )}

      {/* Role-specific sections */}
      {(user.role === 'student' || user.role === 'parent') && renderAttendancePreview()}
      {(user.role === 'student') && renderHomeworkPreview()}
      {(user.role === 'parent' || user.role === 'student') && renderFeesPreview()}

      {/* Bottom padding */}
      <View style={styles.bottomPadding} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  headerLeft: {},
  greeting: {
    fontSize: 14,
    color: '#6B7280',
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  roleBadge: {
    backgroundColor: COLORS.primary + '20',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 6,
    alignSelf: 'flex-start',
  },
  roleText: {
    fontSize: 10,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statCard: {
    width: CARD_WIDTH,
    marginBottom: 12,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
  },
  statContent: {
    padding: 12,
    alignItems: 'center',
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  statIconText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  statInfo: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  section: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 12,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionCard: {
    width: (width - 48) / 2 - 6,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  quickActionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
  },
  quickActionIconText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  quickActionLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
    textAlign: 'center',
  },
  sectionCard: {
    borderRadius: 12,
    marginBottom: 12,
    backgroundColor: '#FFFFFF',
  },
  viewAll: {
    color: COLORS.primary,
    fontSize: 14,
    fontWeight: '600',
  },
  attendanceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  attendanceDay: {
    alignItems: 'center',
  },
  dayName: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  statusDot: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4,
  },
  statusText: {
    fontSize: 10,
    color: '#6B7280',
  },
  homeworkItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  homeworkInfo: {
    flex: 1,
  },
  homeworkTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  homeworkSubject: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeText: {
    fontSize: 11,
    fontWeight: '600',
  },
  feeSummary: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  feeItem: {
    alignItems: 'center',
  },
  feeLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  feeAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  progressBar: {
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
  },
  progressText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
    textAlign: 'center',
  },
  actionCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
  },
  actionContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  actionIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  actionIconText: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  actionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  bottomPadding: {
    height: 20,
  },
});
