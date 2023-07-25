import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import os
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import requests
import pickle
import numpy as np

# Initialize an empty list to store the conversation history
conversation_history = []


def load_data(file_path_or_url):
    if file_path_or_url.endswith('.csv'):
        df = pd.read_csv(file_path_or_url)
    elif file_path_or_url.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path_or_url)
    elif file_path_or_url.endswith('.json'):
        with open(file_path_or_url, 'r') as json_file:
            data = json.load(json_file)
        df = pd.DataFrame(data)
    else:
        df = load_data_from_google_sheets(file_path_or_url)
    return df

def load_data_from_google_sheets(sheet_url):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('your_credentials.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def inspect_data(df):
    print("DataFrame loaded successfully. Here's a preview:")
    print(df.head())
    print("Data columns:")
    print(df.columns)

def create_plot(fig, df, x_column, y_column, plot_type, color, title=None, x_axis_label=None, y_axis_label=None, x_axis_settings=None, y_axis_settings=None):
    plot_types = ['line', 'scatter', 'bar', 'histogram', 'box', 'pie']

    if plot_type not in plot_types:
        print(f"Unsupported plot type. Choose from {plot_types}.")
        return

    if plot_type == 'line':
        fig.add_trace(go.Scatter(x=df[x_column], y=df[y_column], mode='lines', line_shape='linear', marker_color=color, name=y_column))
    elif plot_type == 'scatter':
        fig.add_trace(go.Scatter(x=df[x_column], y=df[y_column], mode='markers', marker_color=color, name=y_column))
    elif plot_type == 'bar':
        fig.add_trace(go.Bar(x=df[x_column], y=df[y_column], marker_color=color, name=y_column))
    elif plot_type == 'histogram':
        fig.add_trace(go.Histogram(x=df[y_column], marker_color=color, name=y_column))
    elif plot_type == 'box':
        fig.add_trace(go.Box(x=df[y_column], marker_color=color, name=y_column))
    elif plot_type == 'pie':
        fig.add_trace(go.Pie(labels=df[x_column], values=df[y_column], marker_colors=color, name=y_column))

    fig.update_layout(
        title=title if title else f"{plot_type.capitalize()} Plot of {y_column} vs {x_column}",
        xaxis_title=x_axis_label if x_axis_label else x_column,
        yaxis_title=y_axis_label if y_axis_label else 'Value',
        legend_title='Legend',
        showlegend=True
    )

    if x_axis_settings:
        fig.update_xaxes(range=[x_axis_settings['min'], x_axis_settings['max']], dtick=x_axis_settings['increment'])

    if y_axis_settings:
        fig.update_yaxes(range=[y_axis_settings['min'], y_axis_settings['max']], dtick=y_axis_settings['increment'])

def create_multi_plots(df):
    num_plots = int(input("How many plots do you want to create? (Enter a number): "))
    if num_plots < 1:
        print("Invalid number of plots. Exiting.")
        return

    subplot_cols = num_plots  # Each plot will be in its own column
    fig = sp.make_subplots(rows=1, cols=subplot_cols)

    for i in range(num_plots):
        x_column = input(f"Enter the column name for the X-axis for plot {i + 1}: ")
        y_column = input(f"Enter the column name for the Y-axis for plot {i + 1}: ")
        plot_type = input(f"Enter the type of plot for plot {i + 1} (line, scatter, bar, histogram, box, pie): ").lower()
        color = input(f"Enter the color for plot {i + 1} (e.g., 'red', '#00FF00', etc.): ")

        create_plot(fig, df, x_column, y_column, plot_type, color)

    customize_labels = input("Do you want to customize the X and Y axis labels, and plot title? (yes/no): ").lower() == 'yes'
    if customize_labels:
        title = input("Enter the title for the plots: ")
        x_axis_label = input("Enter the label for the X-axis: ")
        y_axis_label = input("Enter the label for the Y-axis: ")
    else:
        title, x_axis_label, y_axis_label = None, None, None

    customize_axis_settings = input("Do you want to customize the increment and range of the X and Y axes? (yes/no): ").lower() == 'yes'
    x_axis_settings = get_axis_settings('X') if customize_axis_settings else None
    y_axis_settings = get_axis_settings('Y') if customize_axis_settings else None

    save_plots = input("Do you want to save the plots? (yes/no): ").lower() == 'yes'
    if save_plots:
        format = input("Enter the format of the saved plots (png, jpeg, pdf, svg, etc.): ").lower()
        save_dir = input("Enter the directory where you want to save the plots (leave empty for the current directory): ")

    fig.update_layout(title=title, xaxis_title=x_axis_label, yaxis_title=y_axis_label)

    if x_axis_settings:
        fig.update_xaxes(range=[x_axis_settings['min'], x_axis_settings['max']], dtick=x_axis_settings['increment'])

    if y_axis_settings:
        fig.update_yaxes(range=[y_axis_settings['min'], y_axis_settings['max']], dtick=y_axis_settings['increment'])

    fig.show()

    if save_plots:
        filename = input("Enter the filename to save the plots (leave empty for default name): ")
        for i in range(num_plots):
            if not filename:
                filename = f"{i + 1}_{fig.data[i]['type']}_plot.{format}"
            fig.write_image(os.path.join(save_dir, filename))
            print(f"Figure {i + 1} saved as '{filename}' in directory '{save_dir}'.")
            filename = ""



def get_axis_settings(axis_name):
    customize = input(f"Do you want to customize the {axis_name} axis? (yes/no): ").lower() == 'yes'
    if customize:
        min_val = float(input(f"Enter the minimum value for the {axis_name} axis: "))
        max_val = float(input(f"Enter the maximum value for the {axis_name} axis: "))
        increment = float(input(f"Enter the increment for the {axis_name} axis: "))
        return {'min': min_val, 'max': max_val, 'increment': increment}
    return None

def ask_question(question, df):
    global conversation_history  # Declare conversation_history as a global variable

    # Convert table data to JSON string format
    table_data_json = json.dumps(df.to_dict(orient='split'))

    # Make API request to ChatGPT API
    api_key = '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'  # Replace with your actual API key
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {api_key}'}
    api_url = 'https://api.openai.com/v1/chat/completions'  # API endpoint
    payload = {
        'model': 'gpt-3.5-turbo',  # Use the appropriate GPT-3.5 model name
        'messages': [
            {'role': 'user', 'content': f"Analyze the table data: {table_data_json}"},
            {'role': 'user', 'content': question}
        ]
    }
    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        # Extract answer from API response
        response_data = response.json()
        answer = response_data['choices'][0]['message']['content']
        print("ChatGPT Response:")
        print(answer)

        # Store the conversation message in the history
        conversation_history.append({'user': question, 'chatbot': answer})
    else:
        print(f"Failed to ask question. API request error. Status Code: {response.status_code}")
        print(f"Response Content: {response.content}")

def export_conversation_history(history, filename):
    with open(filename, 'wb') as file:
        pickle.dump(history, file)
    print(f"Conversation history saved to {filename}.")
    

def save_conversation(conversation_history):
    save_option = input("Do you want to save the conversation history? (yes/no): ").lower() == 'yes'
    if not save_option:
        return

    filename = input("Enter the filename to save the conversation history (without extension): ")
    format_option = input("Choose the format to save the conversation history (txt, csv, xlsx, json): ").lower()

    if format_option == 'txt':
        filename += '.txt'
        with open(filename, 'w') as file:
            for msg in conversation_history:
                file.write(f"User: {msg['user']}\n")
                file.write(f"Chatbot: {msg['chatbot']}\n")
                file.write("\n")
        print(f"Conversation history saved as '{filename}'.")
    elif format_option == 'csv':
        filename += '.csv'
        df = pd.DataFrame(conversation_history)
        df.to_csv(filename, index=False)
        print(f"Conversation history saved as '{filename}'.")
    elif format_option == 'xlsx':
        filename += '.xlsx'
        df = pd.DataFrame(conversation_history)
        df.to_excel(filename, index=False)
        print(f"Conversation history saved as '{filename}'.")
    elif format_option == 'json':
        filename += '.json'
        with open(filename, 'w') as file:
            json.dump(conversation_history, file)
        print(f"Conversation history saved as '{filename}'.")
    else:
        print("Invalid format option. Conversation history will not be saved.")
        print("Invalid format option. Conversation history will not be saved.")
    


def advanced_analysis(df):
    print("Available Columns:")
    print(df.columns)
    selected_columns = input("Enter the names of columns for analysis (comma-separated): ").split(',')

    if not all(col.strip() in df.columns for col in selected_columns):
        print("Invalid column name(s).")
        return

    selected_df = df[selected_columns]
    summary_stats = selected_df.describe()

    print("\nSummary Statistics:")
    print(summary_stats)

def display_common_questions():
    common_questions = [
        "What is the average value of column X?",
        "How many unique values are there in column Y?",
        "What is the maximum value in column Z?",
        "Show me a bar chart of the distribution of column A.",
        "Plot a line chart of column B over time (assuming a time-based column).",
        "Can you display a scatter plot between columns C and D?",
        "What is the standard deviation of column E?",
        "Show me the top 10 rows where column F has the highest values.",
        "Provide a summary of descriptive statistics for columns G, H, and I.",
        "Compare the distribution of column J between two different groups (e.g., males and females).",
        "Can you create a pie chart to show the proportion of different categories in column K?",
        "Plot a box plot for column L to identify outliers.",
        "Calculate the correlation coefficient between columns M and N.",
        "Show me the 5th percentile of column O.",
        "What is the median value in column P?"
    ]

    print("\nHere are some common data analysis questions you might find useful:")
    for i, question in enumerate(common_questions, 1):
        print(f"{i}. {question}")

def main():
    file_path = input("Please enter the file path of your data file (CSV or Excel or Google Sheet URL): ")
    df = load_data(file_path)
    inspect_data(df)

    print("Choose the features you want to use (comma-separated numbers):")
    print("1. Normal Plot - Same Type")
    print("2. Multi-Types")
    print("3. Save Processed Data")
    print("4. Ask a question about the data")
    print("5. Save Conversation History")
    print("6. Advanced Analysis")
    print("7. Display Common Questions for Data Analysis")
    print("8. Exit")  
    choice = input("Enter the numbers of the features you want to use: ")

    features = choice.split(',')

    while '8' not in features:
        if '1' in features:
            x_column = input("Enter the column name for the X-axis: ")
            y_column = input("Enter the column name for the Y-axis: ")
            plot_type = input("Enter the type of plot (line, scatter, bar, histogram, box, pie): ").lower()
            color = input("Enter the color for the plot (e.g., 'red', '#00FF00', etc.): ")
            create_plot(go.Figure(), df, x_column, y_column, plot_type, color)

        if '2' in features:
            create_multi_plots(df)

        if '3' in features:
            save_data(df)

        if '4' in features:
            question = input("Enter a question about the data: ")
            ask_question(question, df)

        if '5' in features:
            save_conversation(conversation_history)
            

        if '6' in features:
            advanced_analysis(df)

        if '7' in features:
            display_common_questions()

        print("\nChoose the features you want to use (comma-separated numbers):")
        print("1. Normal Plot - Same Type")
        print("2. Multi-Types")
        print("3. Save Processed Data")
        print("4. Ask a question about the data")
        print("5. Save Conversation History")
        print("6. Advanced Analysis")
        print("7. Display Common Questions for Data Analysis")
        print("8. Exit")
        choice = input("Enter the numbers of the features you want to use: ")
        features = choice.split(',')

if __name__ == "__main__":
    main()
