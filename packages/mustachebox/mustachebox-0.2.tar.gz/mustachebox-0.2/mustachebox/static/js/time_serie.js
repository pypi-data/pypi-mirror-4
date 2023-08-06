// Time serie chart is used by area.js, bar_chart.js and
// column_chart.js Those charts uses the same data structure :
// a year and a serie of number for each row.

function renderTable(data){
// draw a table with the data given in arguments.
    dataset = new google.visualization.DataTable();
    for(var i=0; i< data.label.length; i++){
        if(i == 0){
            // first column is a string type
            dataset.addColumn('string', data.label[i]);
        }else{
            dataset.addColumn('number', data.label[i]);}
    }
    rows = []
    for(var index in data){
        if(index!= 'label'){
            rows.push(data[index])
        }
    }
    // add every rows to the dataset
    dataset.addRows(rows)
    return dataset
};
