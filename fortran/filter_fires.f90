program filter_fires

implicit none
integer :: ios, n_records, n_large
character (len=1000) :: line

real :: acres
character(len=100) :: acres_text
character(len=100) :: incident_type
character(len=100) :: ignition_date
character(len=200) :: fire_name
character(len=100) :: latitude, longitude
integer :: fire_year
integer :: year_index, i
real :: annual_acres(1985:2025)
integer :: annual_fires(1985:2025)

open(unit=10, file='../data/mtbs_fod_points.csv', &
status='old', action='read', iostat=ios)

if (ios /= 0) then
print *, 'Error opening file'
stop
end if

print *, 'File opened successfully'

! Read and print the header
read(10, '(A)', iostat=ios) line

if (ios == 0) then
print *, 'header:'
print *, trim(line)
else
print *, 'error reading header'
end if

! Count all fire records

open(unit=20, file='../output/filtered_fires.csv', &
status='replace', action='write', iostat=ios)

if (ios /= 0) then
print *, 'error opening output file'
stop
end if

write(20, '(A)') 'fire_name,incident_type,acres,latitude,longitude,ignition_date'

n_records = 0
n_large = 0

annual_acres = 0.0
annual_fires = 0

do
read (10, '(A)', iostat=ios) line
if (ios /= 0) exit

n_records = n_records +1

call get_csv_field(line, 8, acres_text)
call get_csv_field(line, 4, incident_type)
call get_csv_field(line, 11, ignition_date)
call get_csv_field(line, 3, fire_name)
call get_csv_field(line, 9, latitude)
call get_csv_field(line, 10, longitude)

! remove quotation marks from acreage
acres_text = adjustl(acres_text(2:len_trim(acres_text)-1))

! read year from ignition date
read(ignition_date(1:4), *, iostat=ios) fire_year

! convert acreage to a number
read(acres_text, *, iostat=ios) acres

! keep only wildfires >= 300 acres from 1985-2025

if (ios == 0) then
if (acres >= 300.0 .and. &
trim(incident_type) == 'Wildfire' .and. &
fire_year >= 1985 .and. fire_year <= 2025) then
n_large = n_large + 1

annual_acres(fire_year) = annual_acres(fire_year) + acres
annual_fires(fire_year) = annual_fires(fire_year) + 1

write(20, '(A,",",A,",",F12.1,",",A,",",A,",",A)') &
    trim(fire_name), trim(incident_type), acres, &
    trim(latitude), trim(longitude), trim(ignition_date)

end if
end if

end do

print *, 'Number of fire records:', n_records
print *, 'Fires >= 300 acres, 1985-2025:', n_large

open(unit=30, file='../output/annual_fire_totals.csv', &
status='replace', action='write')

write(30, '(A)') 'year,total_acres,number_of_fires'

do i = 1985, 2025
write (30, '(I4,",",F15.1,","I8)') &
i, annual_acres(i), annual_fires(i)
end do

close(30)

close(10)
close(20)

contains

subroutine get_csv_field(line, field_number, value)

character(len=*), intent(in) :: line
integer, intent(in) :: field_number
character(len=*), intent(out) :: value

integer :: i, field, start_pos
logical :: in_quotes

value = ''
field = 1
start_pos = 1
in_quotes = .false.

do i = 1, len_trim(line)

if(line(i:i) == '"') then
in_quotes = .not. in_quotes
end if

if(line(i:i) == ',' .and. .not. in_quotes) then
if(field == field_number) then
value = line(start_pos:i-1)
return
end if

field = field + 1
start_pos = i + 1
end if

end do

if (field == field_number) then
value = line (start_pos:len_trim(line))
end if

end subroutine get_csv_field

end program filter_fires

