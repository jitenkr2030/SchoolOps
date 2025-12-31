import React, { useState } from 'react';
import {
  View,
  ScrollView,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  Dimensions,
} from 'react-native';
import {
  Text,
  Card,
  SegmentedButtons,
  Avatar,
  Badge,
  IconButton,
  Surface,
  ProgressBar,
} from 'react-native-paper';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import {
  ATTENDANCE_DATA,
  GRADES_DATA,
  HOMEWORK_DATA,
  TIMETABLE_DATA,
} from '../../services/mockData';
import { formatDate, getStatusColor, formatCurrency } from '../../utils/helpers';
import { COLORS } from '../../theme';

const { width } = Dimensions.get('window');

type TabValue = 'attendance' | 'grades' | 'homework' | 'timetable';

export default function AcademicsScreen() {
  const { user } = useSelector((state: RootState) => state.auth);
  const [activeTab, setActiveTab] = useState<TabValue>('attendance');

  const renderAttendanceItem = ({ item }: { item: typeof ATTENDANCE_DATA[0] }) => (
    <Surface style={styles.listItem} elevation={1}>
      <View style={styles.listItemContent}>
        <View style={styles.listItemLeft}>
          <View style={[styles.dateBadge, { backgroundColor: getStatusColor(item.status) + '20' }]}>
            <Text style={styles.dateDay}>{new Date(item.date).getDate()}</Text>
            <Text style={styles.dateMonth}>{new Date(item.date).toLocaleString('default', { month: 'short' })}</Text>
          </View>
          <View>
            <Text style={styles.listItemTitle}>{item.day}</Text>
            <Text style={styles.listItemSubtitle}>{item.date}</Text>
          </View>
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
    </Surface>
  );

  const renderGradeItem = ({ item }: { item: typeof GRADES_DATA[0] }) => (
    <Card style={styles.cardItem} mode="elevated">
      <Card.Content>
        <View style={styles.gradeRow}>
          <View style={styles.gradeInfo}>
            <Text style={styles.gradeSubject}>{item.subject}</Text>
            <Text style={styles.gradeExam}>{item.examType} • {formatDate(item.date)}</Text>
          </View>
          <View style={styles.scoreContainer}>
            <Text style={styles.scoreValue}>{item.score}</Text>
            <Text style={styles.scoreMax}>/ {item.maxScore}</Text>
          </View>
        </View>
        <View style={styles.gradeFooter}>
          <ProgressBar
            progress={item.score / item.maxScore}
            color={COLORS.primary}
            style={styles.gradeProgress}
          />
          <View style={[styles.gradeBadge, { backgroundColor: getStatusColor(item.grade) + '20' }]}>
            <Text style={[styles.gradeBadgeText, { color: getStatusColor(item.grade) }]}>
              Grade: {item.grade}
            </Text>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderHomeworkItem = ({ item }: { item: typeof HOMEWORK_DATA[0] }) => (
    <Card style={styles.cardItem} mode="elevated">
      <Card.Title
        title={item.title}
        subtitle={`${item.subject} • Due ${formatDate(item.dueDate)}`}
        left={(props) => (
          <Avatar.Icon
            {...props}
            icon="book-open-variant"
            style={{ backgroundColor: COLORS.secondary + '20' }}
          />
        )}
        right={(props) => (
          <Badge
            style={{
              backgroundColor: getStatusColor(item.status) + '20',
            }}
          >
            {item.status}
          </Badge>
        )}
      />
      <Card.Content>
        <Text style={styles.homeworkDescription}>{item.description}</Text>
      </Card.Content>
    </Card>
  );

  const renderTimetableDay = (day: string) => {
    const dayClasses = TIMETABLE_DATA.filter((t) => t.day === day);
    if (dayClasses.length === 0) return null;

    return (
      <View key={day} style={styles.timetableDay}>
        <Text style={styles.timetableDayTitle}>{day}</Text>
        <View style={styles.timetableSlots}>
          {dayClasses.map((slot) => (
            <Card key={slot.id} style={styles.timetableCard} mode="elevated">
              <Card.Content>
                <View style={styles.timetableRow}>
                  <Text style={styles.timetableTime}>{slot.time}</Text>
                  <View style={styles.timetableDetails}>
                    <Text style={styles.timetableSubject}>{slot.subject}</Text>
                    <Text style={styles.timetableRoom}>{slot.className} • {slot.room}</Text>
                  </View>
                </View>
              </Card.Content>
            </Card>
          ))}
        </View>
      </View>
    );
  };

  const tabs = [
    { value: 'attendance', label: 'Attendance', icon: 'calendar-check' },
    { value: 'grades', label: 'Grades', icon: 'star' },
    { value: 'homework', label: 'Homework', icon: 'book-open-variant' },
    { value: 'timetable', label: 'Timetable', icon: 'calendar-clock' },
  ];

  return (
    <View style={styles.container}>
      <SegmentedButtons
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as TabValue)}
        buttons={tabs.map((tab) => ({
          value: tab.value,
          label: tab.label,
          icon: tab.icon,
        }))}
        style={styles.tabBar}
        density="medium"
      />

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {activeTab === 'attendance' && (
          <>
            <View style={styles.summaryCard}>
              <View style={styles.summaryItem}>
                <Text style={styles.summaryValue}>94%</Text>
                <Text style={styles.summaryLabel}>Overall Attendance</Text>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <Text style={[styles.summaryValue, { color: COLORS.present }]}>18</Text>
                <Text style={styles.summaryLabel}>Present</Text>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <Text style={[styles.summaryValue, { color: COLORS.absent }]}>1</Text>
                <Text style={styles.summaryLabel}>Absent</Text>
              </View>
            </View>

            <FlatList
              data={ATTENDANCE_DATA}
              renderItem={renderAttendanceItem}
              keyExtractor={(item) => item.id}
              scrollEnabled={false}
              contentContainerStyle={styles.listContent}
            />
          </>
        )}

        {activeTab === 'grades' && (
          <>
            <View style={styles.summaryCard}>
              <View style={styles.summaryItem}>
                <Text style={styles.summaryValue}>A-</Text>
                <Text style={styles.summaryLabel}>Average Grade</Text>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <Text style={[styles.summaryValue, { color: COLORS.present }]}>88</Text>
                <Text style={styles.summaryLabel}>Avg Score</Text>
              </View>
              <View style={styles.summaryDivider} />
              <View style={styles.summaryItem}>
                <Text style={styles.summaryValue}>5</Text>
                <Text style={styles.summaryLabel}>Subjects</Text>
              </View>
            </View>

            <FlatList
              data={GRADES_DATA}
              renderItem={renderGradeItem}
              keyExtractor={(item) => item.id}
              scrollEnabled={false}
              contentContainerStyle={styles.listContent}
            />
          </>
        )}

        {activeTab === 'homework' && (
          <FlatList
            data={HOMEWORK_DATA}
            renderItem={renderHomeworkItem}
            keyExtractor={(item) => item.id}
            scrollEnabled={false}
            contentContainerStyle={styles.listContent}
          />
        )}

        {activeTab === 'timetable' && (
          <View style={styles.timetableContainer}>
            {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'].map((day) =>
              renderTimetableDay(day)
            )}
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  tabBar: {
    marginHorizontal: 16,
    marginTop: 8,
    marginBottom: 8,
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  summaryCard: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    elevation: 2,
  },
  summaryItem: {
    flex: 1,
    alignItems: 'center',
  },
  summaryDivider: {
    width: 1,
    backgroundColor: '#E5E7EB',
  },
  summaryValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  summaryLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  listContent: {
    paddingBottom: 20,
  },
  listItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 8,
    padding: 12,
  },
  listItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  listItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dateBadge: {
    alignItems: 'center',
    justifyContent: 'center',
    width: 48,
    height: 48,
    borderRadius: 12,
    marginRight: 12,
  },
  dateDay: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  dateMonth: {
    fontSize: 10,
    color: '#6B7280',
    textTransform: 'uppercase',
  },
  listItemTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  listItemSubtitle: {
    fontSize: 12,
    color: '#6B7280',
  },
  cardItem: {
    marginBottom: 12,
    borderRadius: 12,
  },
  gradeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  gradeInfo: {
    flex: 1,
  },
  gradeSubject: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
  },
  gradeExam: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2,
  },
  scoreContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  scoreValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: COLORS.primary,
  },
  scoreMax: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  gradeFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  gradeProgress: {
    flex: 1,
    height: 6,
    borderRadius: 3,
    marginRight: 12,
  },
  gradeBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  gradeBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  homeworkDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8,
  },
  timetableContainer: {
    paddingBottom: 20,
  },
  timetableDay: {
    marginBottom: 16,
  },
  timetableDayTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8,
    paddingHorizontal: 4,
  },
  timetableSlots: {
    gap: 8,
  },
  timetableCard: {
    borderRadius: 12,
  },
  timetableRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timetableTime: {
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.primary,
    width: 80,
  },
  timetableDetails: {
    flex: 1,
  },
  timetableSubject: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
  },
  timetableRoom: {
    fontSize: 12,
    color: '#6B7280',
  },
});
