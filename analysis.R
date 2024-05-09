library(dplyr)
library(lubridate) 
library(ggplot2)

data <- read.csv("articles_analyzed.csv", encoding="UTF-8")






library(ggplot2)
library(gridExtra)
library(ggrepel)
library(showtext)

font_add_google("EB Garamond")
showtext_auto()

# GET quarterly analysis
# Convert Date column to Date format
data$Date <- as.Date(data$Date)

# Extract quarter of the year
data$Year <-year(data$Date)

yearly_data <- data %>%
  group_by(Year, Country) %>%
  summarise(Article_Count = n())

yearly_data$Country <- factor(yearly_data$Country, levels = c("Austria", "Hungary", "Czechia"))


# Plot yearly article counts for each country
ggplot(yearly_data, aes(x = Year, y = Article_Count, fill = Country)) +
  geom_bar(stat = "identity", position = "dodge") +
  labs(x = "Year",
       y = "Article Count",
       color = "Country",
       fill = NULL) +
  scale_fill_manual(values = c("#ef476f", "#06d6a0", "#073b4c")) +  # Change the colors here
  theme_minimal() +
  theme(
    legend.position = "right",
    text=element_text(family="EB Garamond", size=35),
    axis.title.x = element_text(face="bold"),
    axis.title.y = element_text(face="bold"))
  )
















positive_data <- data %>%
  filter(data[[8]] == 1 | data[[9]] == 1 | data[[10]] == 1) %>%
  select(Year, Country)

negative_data <- data %>%
  filter(data[[11]] == 1 | data[[12]] == 1 | data[[13]] == 1 | data[[14]] == 1 | data[[15]] == 1 | data[[16]] == 1) %>%
  select(Year, Country)

# Aggregate data to get yearly article counts for each country for positive and negative articles
positive_yearly_data <- positive_data %>%
  group_by(Year, Country) %>%
  summarise(Article_Count = n())

negative_yearly_data <- negative_data %>%
  group_by(Year, Country) %>%
  summarise(Article_Count = n())

# Plot yearly article counts for each country for positive and negative articles
plot_positive <- ggplot(positive_yearly_data, aes(x = Year, y = Article_Count, color = Country)) +
  geom_line() +
  labs(title = "Yearly Positive Article Counts by Country",
       x = "Year",
       y = "Article Count",
       color = "Country") +
  theme_minimal()

plot_negative <- ggplot(negative_yearly_data, aes(x = Year, y = Article_Count, color = Country)) +
  geom_line() +
  labs(x = "Year",
       y = "Article Count",
       color = "Country") +
  theme_minimal()

# Print the plots
print(plot_positive)
print(plot_negative)


















# GET salience of different flashpoints
colnames(data)[7] <- "about country"
colnames(data)[8] <- "Boosting tourism"
colnames(data)[9] <- "Economic opportunity"
colnames(data)[10] <- "Positive competition"
colnames(data)[11] <- "Licensing"
colnames(data)[12] <- "Negative competition"
colnames(data)[13] <- "Disturbance of locals"
colnames(data)[14] <- "Taxation"
colnames(data)[15] <- "Long term housing"
colnames(data)[16] <- "Gentrification"

for (i in 7:16) {
  data[, i] <- ifelse(grepl("1", data[, i]), "1", ifelse(grepl("0", data[, i]), "0", data[, i]))
  print(colnames(data)[i])
  print(table(data[i]))
}

data <- data[data$`about country` == 1,]

table(data$Country)

result <- aggregate(. ~ Country, data, function(x) sum(x == 1) / length(x))

# Showing the result
print(result)


# Create an empty plot
par(family = "serif", mfrow=c(3, 3), font.main = 2, font.axis = 1, cex.lab=1.5, cex.axis=1.4, cex.main=2.2)  # Adjust rows and columns as needed
par(family = "serif", font = 2, font.lab = 1, font.axis = 1, cex.lab=1.3, cex.axis=1.3, cex.main=1.3, cex.sub=1.3)



# Iterate over each column and create a barplot
for (i in 8:16) {  # Start from 2 to skip the first column 'Country'
  barplot(result[, i] ~ result$Country, main=colnames(result)[i], xlab="", ylab="", ylim=c(0, 0.5))
}

# Reset the plotting parameters to default
par(mfrow=c(1, 1))
